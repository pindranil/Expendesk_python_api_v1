# import os

# from openai import OpenAI
# from pydantic import BaseModel,Field
# from typing import Optional,List, Union
# import ast
# import json


# from dotenv import load_dotenv

# load_dotenv()

# openai_api_key = os.getenv("OPENAI_SECRET_KEY")

# client = OpenAI(api_key=openai_api_key)

# class LineItemEntry(BaseModel):
#     date: str
#     description: str
#     amount: str
#     SAC_code: str

# class LineItemArray(BaseModel):
#     data: List[LineItemEntry]

# class LiquorItems(BaseModel):
#     liquor_name: str
#     liquor_amount: str

# class DataFieldsFood(BaseModel):
#     merchant_name: str
#     invoice_no: str
#     total_amount: str
#     invoice_date: str
#     sgst_amount: str
#     cgst_amount: str
#     liquor_details: List[LiquorItems] = Field(description="List of liquor items with their names and amounts if liquor is present otherwise return empty list, do not include non-liquor items")

# class DataFieldsTravel(BaseModel):
#     merchant_name: str
#     invoice_no: str
#     total_amount: str
#     invoice_date: str
#     sgst_amount: str
#     cgst_amount: str
#     mode_of_travel: str
#     travel_ticket_class: str
#     from_location: str
#     to_location: str
#     departure_date: str
#     departure_time: str
#     arrival_date: str
#     arrival_time: str
#     no_of_km: str
#     intra_or_inter_city_travel: str = Field( description=(
#         "List of actual service items billed by the hotel such as room tariff, "
#         "in-room dining, room service, laundry, etc., each with date, description, amount, and SAC_code. "
#         "⚠️ Do NOT include tax lines like 'State GST' or 'Central GST'. "
#         "Example valid entry: {\"date\": \"02/06/23\", \"description\": \"TARIFF / Room\", \"amount\": \"4500.00\", \"SAC_code\": \"996311\"}"
#     ))

# class DataFieldsHotel(BaseModel):
#     merchant_name: str
#     invoice_no: str
#     total_amount: str
#     invoice_date: str
#     sgst_amount: str
#     cgst_amount: str
#     company_name: str
#     gst_no: str
#     guest_name: str
#     checkin_date: str
#     checkout_date: str
#     total_days_stayed: str
#     hotel_state: str
#     hotel_city: str
#     hotel_pin: str
#     hotel_service_breakage: List[LineItemEntry] = Field(description="List of service breakage items with their names and amounts and date")


# def print_all_fields(user_input: str, invoice_type: str) -> Union[DataFieldsFood, DataFieldsTravel, DataFieldsHotel]:
#     # Determine the response format based on invoice_type
#     response_format = {
#         "food": DataFieldsFood,
#         "travel": DataFieldsTravel,
#         "hotel": DataFieldsHotel
#     }.get(invoice_type.lower())
    
#     if not response_format:
#         raise ValueError(f"Invalid invoice type: {invoice_type}. Supported types are: food, travel, hotel")

#     completion = client.beta.chat.completions.parse(
#        model="gpt-4o",
#         messages=[
#             {"role": "system", "content": f"Extract the {invoice_type} invoice information."},
#             {"role": "user", "content": user_input},
#         ],
#         response_format=response_format,
#     )
    
#     # Parse the JSON response into the appropriate model
#     response_data = completion.choices[0].message.parsed
    
    
#     return response_data

# def convert_to_jsonHotel(hotel_data: DataFieldsHotel) -> dict:
#     data =  hotel_data.model_dump_json(indent=2)
#     return json.loads(data)

# def convert_to_jsonTravel(travel_data: DataFieldsTravel) -> dict:
#     data= travel_data.model_dump_json(indent=2)
#     return json.loads(data)

# def convert_to_jsonFood(food_data: DataFieldsFood) -> dict:
#     data= food_data.model_dump_json(indent=2)
#     return json.loads(data)

# def convert_to_json(data: Union[DataFieldsFood, DataFieldsTravel, DataFieldsHotel]) -> dict:
#     if isinstance(data, DataFieldsFood):
#         return convert_to_jsonFood(data)
#     elif isinstance(data, DataFieldsTravel):
#         return convert_to_jsonTravel(data)
#     elif isinstance(data, DataFieldsHotel):
#         return convert_to_jsonHotel(data)
#     else:
#         raise ValueError("Unsupported data type for conversion to JSON.")
    
# class InvoiceParser:
#     def __init__(self, invoice_type: str, user_input: str):
#         self.invoice_type = invoice_type
#         self.user_input = user_input
        
#     def parse(self) -> dict:
#         parsed_data = print_all_fields(self.user_input, self.invoice_type)
#         print("parsed_data",parsed_data)
#         json_data = convert_to_json(parsed_data)
#         return json_data

import os

from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional, List, Union
import ast
import json

from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_SECRET_KEY")

client = OpenAI(api_key=openai_api_key)

class LineItemEntry(BaseModel):
    date: str
    description: str
    amount: str
    SAC_code: str

class LineItemArray(BaseModel):
    data: List[LineItemEntry]

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
    liquor_details: List[LiquorItems] = Field(
        description="List of liquor items with their names and amounts if liquor is present otherwise return empty list, do not include non-liquor items"
    )

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
    intra_or_inter_city_travel: str

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
    hotel_service_breakage: List[LineItemEntry] = Field(
        description=(
            "CRITICAL: Extract ONLY actual hotel services from the invoice, NOT tax lines. "
            "Include services like: Room Tariff, In-Room Dining, Room Service, Laundry, Spa Services, etc. "
            "⚠️ EXCLUDE ALL TAX ENTRIES: Do NOT include 'SGST', 'CGST', 'State GST', 'Central GST', 'IGST', or any tax-related lines. "
            "⚠️ EXCLUDE percentage-based descriptions like 'Central GST @ 6.00%' or 'State GST @ 9.00%'. "
            "Each entry must have: date, description (service name), amount (service amount before tax), SAC_code. "
            "Example CORRECT entries: "
            "- {'date': '02/06/23', 'description': 'Room Tariff', 'amount': '4500.00', 'SAC_code': '996311'} "
            "- {'date': '02/06/23', 'description': 'In Room Dining', 'amount': '1444.90', 'SAC_code': '996332'}"
        )
    )


def print_all_fields(user_input: str, invoice_type: str) -> Union[DataFieldsFood, DataFieldsTravel, DataFieldsHotel]:
    # Determine the response format based on invoice_type
    response_format = {
        "food": DataFieldsFood,
        "travel": DataFieldsTravel,
        "hotel": DataFieldsHotel
    }.get(invoice_type.lower())
    
    if not response_format:
        raise ValueError(f"Invalid invoice type: {invoice_type}. Supported types are: food, travel, hotel")

    # Create specialized system prompts based on invoice type
    if invoice_type.lower() == "hotel":
        system_content = (
            "You are a hotel invoice data extraction specialist. "
            "Extract hotel invoice information accurately. "
            "For hotel_service_breakage, focus ONLY on actual services provided by the hotel. "
            "NEVER include tax lines, GST entries, or any tax-related items in the service breakage list. "
            "Look for services like room charges, dining, room service, laundry, etc. "
            "Exclude any line items that mention GST, tax, SGST, CGST, or percentage rates."
        )
    elif invoice_type.lower() == "travel":
        system_content = f"You are a travel invoice data extraction specialist. Extract the {invoice_type} invoice information accurately."
    else:  # food
        system_content = (
            "You are a food invoice data extraction specialist. "
            "Extract food invoice information accurately. "
            "For liquor_details, only include items that are clearly alcoholic beverages."
        )

    completion = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_input},
        ],
        response_format=response_format,
    )
    
    # Parse the JSON response into the appropriate model
    response_data = completion.choices[0].message.parsed
    
    return response_data

def convert_to_jsonHotel(hotel_data: DataFieldsHotel) -> dict:
    data = hotel_data.model_dump_json(indent=2)
    return json.loads(data)

def convert_to_jsonTravel(travel_data: DataFieldsTravel) -> dict:
    data = travel_data.model_dump_json(indent=2)
    return json.loads(data)

def convert_to_jsonFood(food_data: DataFieldsFood) -> dict:
    data = food_data.model_dump_json(indent=2)
    return json.loads(data)

def convert_to_json(data: Union[DataFieldsFood, DataFieldsTravel, DataFieldsHotel]) -> dict:
    if isinstance(data, DataFieldsFood):
        return convert_to_jsonFood(data)
    elif isinstance(data, DataFieldsTravel):
        return convert_to_jsonTravel(data)
    elif isinstance(data, DataFieldsHotel):
        return convert_to_jsonHotel(data)
    else:
        raise ValueError("Unsupported data type for conversion to JSON.")

class InvoiceParser:
    def __init__(self, invoice_type: str, user_input: str):
        self.invoice_type = invoice_type
        self.user_input = user_input
        
    def parse(self) -> dict:
        parsed_data = print_all_fields(self.user_input, self.invoice_type)
        print("parsed_data", parsed_data)
        json_data = convert_to_json(parsed_data)
        
        # Post-processing cleanup for hotel invoices to ensure no tax lines slip through
        if self.invoice_type.lower() == "hotel" and "hotel_service_breakage" in json_data:
            filtered_services = []
            tax_keywords = ['gst', 'sgst', 'cgst', 'igst', 'tax', 'central gst', 'state gst', '@', '%']
            
            for service in json_data["hotel_service_breakage"]:
                description_lower = service.get("description", "").lower()
                # Skip if description contains tax-related keywords
                if not any(keyword in description_lower for keyword in tax_keywords):
                    filtered_services.append(service)
                else:
                    print(f"Filtered out tax line: {service.get('description')}")
            
            json_data["hotel_service_breakage"] = filtered_services
        
        return json_data