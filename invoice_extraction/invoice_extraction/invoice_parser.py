from pydantic import BaseModel, Field
from typing import List


class LineItemEntry(BaseModel):
    item_date: str = ""
    description: str = ""
    bill_type: str = ""
    amount: str = ""
    sac_code: str = ""
    sgst_amount: str = ""
    cgst_amount: str = ""


class LiquorItems(BaseModel):
    description: str = ""
    amount: str = ""


class UnauthorizedLineItem(BaseModel):
    """Generic unauthorized item — used for liquor, spa, laundry, etc."""
    description: str = ""
    amount: str = ""


class InvoiceResponse(BaseModel):
    # ── invoice type ───────────────────────────────────────────
    invoice_type: str = Field(
        default="",
        description=(
            "Type of invoice. Must exactly match one of the expense_type values "
            "provided in the system prompt (e.g. 'Hotel', 'Food', 'Travel', 'Miscellaneous')."
        )
    )

    merchant_name: str = ""
    invoice_no: str = ""
    total_amount: str = ""
    # currency_code: str = ""
    invoice_date: str = ""
    sgst_amount: str = ""
    cgst_amount: str = ""

    liquor_items: List[LiquorItems] = Field(
        default_factory=list,
        description="Alcoholic beverages detected in the invoice. Empty list if none."
    )
    # additional_items: List[UnauthorizedLineItem] = Field(
    #     default_factory=list,
    #     description=(
    #         "Additional unauthorized services (e.g. spa, laundry) detected in the invoice. "
    #         "Empty list if none."
    #     )
    # )

    guest_company_name: str = ""
    guest_company_gst_no: str = ""
    vendor_company_gst_no: str = ""
    guest_name: str = ""
    check_in_date: str = ""
    check_out_date: str = ""
    total_days_stayed: str = ""
    service_breakage: List[LineItemEntry] = Field(
        default_factory=list,
        description=(
            "ONLY actual hotel services like Room Tariff, In-Room Dining, Room Service, Laundry, Spa. "
            "EXCLUDE ALL tax lines: SGST, CGST, State GST, Central GST, IGST, or any @ percentage entries."
        )
    )

    mode_of_travel: str = ""
    travel_class: str = ""
    from_location: str = ""
    to_location: str = ""
    departure_date: str = ""
    departure_time: str = ""
    arrival_date: str = ""
    arrival_time: str = ""
    distance: str = ""
    intra_inter_city: str = ""

    state: str = ""
    city: str = ""
    pincode: str = ""