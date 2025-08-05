# invoice_parser.py

import json
from typing import Union, List
from pydantic import BaseModel, Field
from openai import OpenAI

# Initialize OpenAI (you can optionally pass the key from outside too)
import os
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_SECRET_KEY")
if not openai_api_key:
    raise EnvironmentError("Missing OPENAI_SECRET_KEY in .env")

client = OpenAI(api_key=openai_api_key)

# ---------------------- Models ----------------------

class LineItemEntry(BaseModel):
    date: str
    description: str
    amount: str
    SAC_code: str

class LiquorItems(BaseModel):
    liquor_name: str
    liquor_amount: str

class DataFieldsFood(BaseModel):
    merchant_name: str
    invoice_no: str
    total_amount: str
    invoice_date: str
    sgst_amount: str
    cgst_amount: str
    liquor_details: List[LiquorItems] = Field(description="List of liquor items with their names and amounts if liquor is present otherwise return empty list")

class DataFieldsTravel(BaseModel):
    merchant_name: str
    invoice_no: str
    total_amount: str
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
    intra_or_inter_city_travel: str = Field(description="The value will be either 'intra' or 'inter' depending on the travel type")

class DataFieldsHotel(BaseModel):
    merchant_name: str
    invoice_no: str
    total_amount: str
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
    hotel_service_breakage: List[LineItemEntry] = Field(description="List of service breakage items with their names and amounts and date")

# ---------------------- Utilities ----------------------

def print_all_fields(user_input: str, invoice_type: str) -> Union[DataFieldsFood, DataFieldsTravel, DataFieldsHotel]:
    response_format = {
        "food": DataFieldsFood,
        "travel": DataFieldsTravel,
        "hotel": DataFieldsHotel
    }.get(invoice_type.lower())

    if not response_format:
        raise ValueError(f"Invalid invoice type: {invoice_type}. Supported types: food, travel, hotel")

    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"Extract the {invoice_type} invoice information."},
            {"role": "user", "content": user_input},
        ],
        response_format=response_format,
    )

    return completion.choices[0].message.parsed

def convert_to_json(data: Union[DataFieldsFood, DataFieldsTravel, DataFieldsHotel]) -> dict:
    return json.loads(data.model_dump_json(indent=2))

# ---------------------- Main Parser ----------------------

class InvoiceParser:
    def __init__(self, invoice_type: str, user_input: str):
        self.invoice_type = invoice_type
        self.user_input = user_input

    def parse(self) -> dict:
        parsed_data = print_all_fields(self.user_input, self.invoice_type)
        return convert_to_json(parsed_data)
