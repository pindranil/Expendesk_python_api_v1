# invoice_models.py
from pydantic import BaseModel, Field
from typing import List, Union

class LineItemEntry(BaseModel):
    item_date: str
    description: str
    bill_type: str
    amount: str
    sac_code: str
    sgst_amount: str
    cgst_amount: str

class LiquorItems(BaseModel):
    description: str
    amount: str

class DataFieldsFood(BaseModel):
    merchant_name: str
    invoice_no: str
    total_amount_base: str
    currency_code: str
    invoice_date: str
    sgst_amount: str
    cgst_amount: str
    # converted_amount_inr:float
    # exchange_rate_used:float
    liquor_items: List[LiquorItems] = Field(
        description="List of liquor items with their names and amounts if liquor is present otherwise return empty list"
    )
class DataFieldsOthers(BaseModel):
    merchant_name: str
    invoice_no: str
    total_amount_base: str
    currency_code: str
    invoice_date: str
    sgst_amount: str
    cgst_amount: str
    # company_name: str
    # gst_no: str
    state: str
    city: str
    pincode: str
    liquor_items: List[LiquorItems] = Field(
        description="List of liquor items with their names and amounts if liquor is present otherwise return empty  list"
    )
    # converted_amount_inr:float
    # exchange_rate_used:float

class DataFieldsTravel(BaseModel):
    merchant_name: str
    invoice_no: str
    total_amount_base: str
    currency_code: str
    invoice_date: str
    sgst_amount: str
    cgst_amount: str
    mode_of_travel: str
    travel_class: str
    from_location: str
    to_location: str
    departure_date: str
    departure_time: str
    arrival_date: str
    arrival_time: str
    distance: str
    intra_inter_city: str
    liquor_items:List[LiquorItems] = Field(
        description="List of liquor items with their names and amounts if liquor is present otherwise return empty list"
    )

class DataFieldsHotel(BaseModel):
    merchant_name: str
    invoice_no: str
    total_amount_base: str
    currency_code: str
    invoice_date: str
    sgst_amount: str
    cgst_amount: str
    guest_company_name: str
    guest_company_gst_no: str
    guest_name: str
    check_in_date: str
    check_out_date: str
    total_days_stayed: str
    state: str
    city: str
    pincode: str
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
