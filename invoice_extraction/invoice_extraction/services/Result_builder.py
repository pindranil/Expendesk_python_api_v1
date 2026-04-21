from invoice_extraction.invoice_parser import InvoiceResponse, LiquorItems, UnauthorizedLineItem
from invoice_extraction.services.calculate_cost import calculate_token_costs, calculate_total_cost


# Map field name → Pydantic model class
_FIELD_MODEL_MAP = {
    "liquor_items":     LiquorItems,
    "additional_items": UnauthorizedLineItem,
}


def filter_hotel_services(services: list[dict]) -> list[dict]:
    """Remove standalone tax lines from hotel service breakage."""
    exclude_patterns = [
        'central gst @', 'state gst @', 'sgst @', 'cgst @',
        'igst @', 'gst @', 'tax @', 'total tax', 'tax total'
    ]
    return [
        service for service in services
        if not any(
            pattern in service.get("description", "").lower()
            for pattern in exclude_patterns
        )
    ]


def merge_unauthorized_results(invoice_data: InvoiceResponse, unauth_results: dict) -> None:
    """Merge detected unauthorized items back into the invoice model in-place."""
    for field_key, items in unauth_results.items():
        if not hasattr(invoice_data, field_key):
            print(f"[WARN] Field '{field_key}' not in InvoiceResponse model — skipping merge.")
            continue

        model_class = _FIELD_MODEL_MAP.get(field_key)
        if model_class:
            # Convert plain dicts → proper Pydantic model instances to avoid serialization warnings
            typed_items = [
                model_class(
                    description=entry.get("description", ""),
                    amount=entry.get("amount", ""),
                )
                for entry in (items or [])
            ]
        else:
            typed_items = items  # unknown field, assign as-is

        setattr(invoice_data, field_key, typed_items)


def build_result_dict(
    invoice_data:      InvoiceResponse,
    image_file_name:   str,
    combined_prompt:   str,
    total_image_cost:  float,
    extra_token_costs: float = 0.0,
) -> dict:
    """
    Convert InvoiceResponse → final response dict with cost metadata.
    Cleans hotel service breakage and removes internal discriminator fields.
    """
    detected_type = invoice_data.invoice_type
    invoice_dict  = invoice_data.model_dump()

    # Clean hotel services (remove tax lines)
    if detected_type.lower() in ("hotel", "accommodation"):
        raw_services = invoice_dict.get("hotel_service_breakage") or invoice_dict.get("service_breakage") or []
        if raw_services:
            invoice_dict["service_breakage"] = filter_hotel_services(raw_services)
            invoice_dict.pop("hotel_service_breakage", None)

    # Remove Pydantic discriminator field
    invoice_dict.pop("type", None)

    # Cost breakdown
    input_cost, output_cost, input_tokens, output_tokens = calculate_token_costs(
        combined_prompt, invoice_dict
    )
    total_cost_usd, total_cost_inr = calculate_total_cost(
        total_image_cost, input_cost, output_cost, extra_token_costs
    )

    invoice_dict.update({
        "file_name":    image_file_name,
        "invoice_type": detected_type,
        # "estimated_cost_usd":   total_cost_usd,
        # "estimated_cost_inr":   total_cost_inr,
        # "image_cost_usd":       round(total_image_cost, 6),
        # "input_token_cost_usd": round(input_cost, 6),
        # "output_token_cost_usd":round(output_cost, 6),
        # "input_tokens":         input_tokens,
        # "output_tokens":        output_tokens,
    })

    print("invoice_data:", invoice_dict)
    return invoice_dict