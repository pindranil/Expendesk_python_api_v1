import json
from openai import AsyncOpenAI
from invoice_extraction.invoice_parser import InvoiceResponse


async def extract_invoice_single(
    client: AsyncOpenAI,
    base64_image: str,
    combined_prompt: str,
) -> InvoiceResponse:
    """Single image → one structured API call."""
    response = await client.beta.chat.completions.parse(
        model="gpt-5.4-mini",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": combined_prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}",
                        "detail": "high"
                    }
                }
            ]
        }],
        response_format=InvoiceResponse,
        max_completion_tokens=8000,
        reasoning_effort="low",
    )
    return response.choices[0].message.parsed


async def extract_invoice_pdf(
    client: AsyncOpenAI,
    pdf_page_images: list[dict],
    combined_prompt: str,
) -> InvoiceResponse:
    """Multi-page PDF → all pages in one structured API call."""
    content = [{"type": "text", "text": combined_prompt}]
    for page in pdf_page_images:
        content.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{page['base64']}",
                "detail": "high"
            }
        })

    response = await client.beta.chat.completions.parse(
        model="gpt-5.4-mini",
        messages=[{"role": "user", "content": content}],
        response_format=InvoiceResponse,
        max_completion_tokens=8000,
        reasoning_effort="low",
    )
    return response.choices[0].message.parsed


async def detect_unauthorized_items(
    client: AsyncOpenAI,
    image_contents: list[dict],
    unauthorized_items: list[dict],
    pricing: dict,
    extra_cost_accumulator: list,
) -> dict:
    """
    For each unauthorized_item config, run a separate AI call using its own
    system_prompt and output_format. Returns a merged dict keyed by output field name.

    unauthorized_items DB schema:
      [
        {
          "unauthorized_item_id": 1,
          "item_name": "Liquor",
          "item_description": "Whiskey,Gin,Vodka,Beer,Cocktail",
          "system_prompt": "you are an expert...",
          "output_format": '{"liquor_items": [{"item": "item_name", "price": "price"},..]}'
        },
        ...
      ]

    Returns e.g.:
      {
        "liquor_items":     [{"description": "Whiskey", "amount": "450.00"}],
        "additional_items": [{"description": "Spa",     "amount": "1200.00"}]
      }
    """
    merged_results: dict = {}

    for unauth in unauthorized_items:
        item_name     = unauth.get("item_name", "")
        system_prompt = unauth.get("system_prompt", "")
        output_format = unauth.get("output_format", "{}")

        if not system_prompt:
            print(f"[WARN] No system_prompt for unauthorized item '{item_name}', skipping.")
            continue

        user_prompt = (
            f"{system_prompt}\n\n"
            f"Return ONLY valid JSON matching this exact format (no extra keys, no markdown):\n"
            f"{output_format}\n\n"
            f"If no such items are found, return empty lists in the same format."
        )

        content = [{"type": "text", "text": user_prompt}] + image_contents

        try:
            response = await client.chat.completions.create(
                model="gpt-5.4-mini",
                messages=[{"role": "user", "content": content}],
                max_completion_tokens=2000,
                reasoning_effort="low",
            )

            raw_text = response.choices[0].message.content or ""
            print(f"[DEBUG] Unauthorized '{item_name}' raw response: {raw_text[:200]}")

            # Strip markdown fences if present
            cleaned = raw_text.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("```")[1]
                if cleaned.startswith("json"):
                    cleaned = cleaned[4:]
                cleaned = cleaned.strip()

            parsed: dict = json.loads(cleaned)

            # Normalise item/price → description/amount
            for key, items_list in parsed.items():
                merged_results[key] = [
                    {
                        "description": entry.get("item",  entry.get("description", "")),
                        "amount":      entry.get("price", entry.get("amount", "")),
                    }
                    for entry in (items_list or [])
                ]

            # Accumulate extra token cost
            if response.usage:
                extra_cost_accumulator.append(
                    response.usage.prompt_tokens     * pricing["input_token"] +
                    response.usage.completion_tokens * pricing["output_token"]
                )

        except json.JSONDecodeError as je:
            print(f"[ERROR] JSON parse failed for '{item_name}': {je}")
            merged_results[_key_for_item(item_name)] = []
        except Exception as e:
            print(f"[ERROR] Unauthorized item detection failed for '{item_name}': {e}")
            merged_results[_key_for_item(item_name)] = []

    return merged_results


def _key_for_item(item_name: str) -> str:
    return item_name.lower().replace(" ", "_")