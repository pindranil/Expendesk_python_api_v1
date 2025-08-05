# invoice_models.py
from pydantic import BaseModel, Field
from typing import List, Union

class LineItemEntry(BaseModel):
    date: str
    description: str
    type: str
    amount: str
    SAC_code: str
    sgst_amount: str
    cgst_amount: str

class LiquorItems(BaseModel):
    liquor_name: str
    liquor_amount: str

class DataFieldsFood(BaseModel):
    merchant_name: str
    invoice_no: str
    total_amount: str
    currency_code: str
    invoice_date: str
    sgst_amount: str
    cgst_amount: str
    # converted_amount_inr:float
    # exchange_rate_used:float
    liquor_details: List[LiquorItems] = Field(
        description="List of liquor items with their names and amounts if liquor is present otherwise return empty list"
    )
class DataFieldsOthers(BaseModel):
    merchant_name: str
    invoice_no: str
    total_amount: str
    currency_code: str
    invoice_date: str
    sgst_amount: str
    cgst_amount: str
    company_name: str
    gst_no: str
    state: str
    city: str
    pin: str
    # converted_amount_inr:float
    # exchange_rate_used:float

class DataFieldsTravel(BaseModel):
    merchant_name: str
    invoice_no: str
    total_amount: str
    currency_code: str
    invoice_date: str
    sgst_amount: str
    cgst_amount: str
    mode_of_travel: str
    travel_ticket_class: str
    from_location: str
    to_location: str
    departure_date: str
    departure_time: str
    arrival_date: str
    arrival_time: str
    no_of_km: str
    intra_or_inter_city_travel: str

class DataFieldsHotel(BaseModel):
    merchant_name: str
    invoice_no: str
    total_amount: str
    currency_code: str
    invoice_date: str
    sgst_amount: str
    cgst_amount: str
    company_name: str
    gst_no: str
    guest_name: str
    checkin_date: str
    checkout_date: str
    total_days_stayed: str
    hotel_state: str
    hotel_city: str
    hotel_pin: str
    # converted_amount_inr:float
    # exchange_rate_used:float
    hotel_service_breakage: List[LineItemEntry] = Field(
        description=(
            "ONLY actual hotel services like Room Tariff, In-Room Dining, Room Service, Laundry, Spa. "
            "EXCLUDE ALL tax lines: SGST, CGST, State GST, Central GST, IGST, or any @ percentage entries."
        )
    )

class InvoiceResponse(BaseModel):
    invoice_type: str = Field(description="Type of invoice: hotel, travel,food, or others")
    data: Union[DataFieldsHotel, DataFieldsTravel, DataFieldsFood,DataFieldsOthers] = Field(
        description="Invoice data based on the invoice type"
    )
