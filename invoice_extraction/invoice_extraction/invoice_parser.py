# invoice_models.py
from pydantic import BaseModel, Field
from typing import List, Optional

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

class InvoiceResponse(BaseModel):
    # ── invoice type ───────────────────────────────────────────
    invoice_type: str = Field(
        default="",
        description="Type of invoice: hotel, travel, food, or others"
    )

    # ── common fields (all types) ──────────────────────────────
    merchant_name: str = ""
    invoice_no: str = ""
    total_amount_base: str = ""
    currency_code: str = ""
    invoice_date: str = ""
    sgst_amount: str = ""
    cgst_amount: str = ""
    liquor_items: List[LiquorItems] = Field(
        default_factory=list,
        description="List of liquor items if present, otherwise empty list"
    )

    # ── hotel-only fields ──────────────────────────────────────
    guest_company_name: str = ""
    guest_company_gst_no: str = ""
    guest_name: str = ""
    check_in_date: str = ""
    check_out_date: str = ""
    total_days_stayed: str = ""
    hotel_service_breakage: List[LineItemEntry] = Field(
        default_factory=list,
        description=(
            "ONLY actual hotel services like Room Tariff, In-Room Dining, Room Service, Laundry, Spa. "
            "EXCLUDE ALL tax lines: SGST, CGST, State GST, Central GST, IGST, or any @ percentage entries."
        )
    )

    # ── travel-only fields ─────────────────────────────────────
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

    # ── hotel + others fields ──────────────────────────────────
    state: str = ""
    city: str = ""
    pincode: str = ""