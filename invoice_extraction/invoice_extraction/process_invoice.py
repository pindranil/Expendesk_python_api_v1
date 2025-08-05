
import io
import os
import base64
import asyncio
from PIL import Image
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI
from invoice_extraction.invoice_parser_v1 import InvoiceResponse
from invoice_extraction.conversion import fetch_conversion_rate

load_dotenv()
openai_api_key = os.getenv("OPENAI_SECRET_KEY")
if not openai_api_key:
    raise EnvironmentError("Missing OPENAI_SECRET_KEY in .env")


USD_TO_INR = 83.0

client = AsyncOpenAI(api_key=openai_api_key)


class AsyncImageProcessor:
    def __init__(self):
        self.client = client
        self.usd_to_inr = USD_TO_INR

    def resize_image_if_needed(self, image_bytes, max_dimension=1024):
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode != "RGB":
            image = image.convert("RGB")

        width, height = image.size
        if width > max_dimension or height > max_dimension:
            if width > height:
                new_width = max_dimension
                new_height = int((height * max_dimension) / width)
            else:
                new_height = max_dimension
                new_width = int((width * max_dimension) / height)
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            width, height = new_width, new_height

        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG', quality=75, optimize=True)
        return img_byte_arr.getvalue(), width, height

    def encode_image_to_base64(self, image_bytes):
        return base64.b64encode(image_bytes).decode("utf-8")

    def calculate_image_cost(self, width, height):
        return 0.00025 if width < 720 and height < 720 else 0.001

    async def detect_invoice_type(self, base64_image, type_prompt):
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": type_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }],
            max_tokens=50,
            temperature=0.0,
        )
        return response.choices[0].message.content.strip().lower()

    async def extract_invoice_data(self, base64_image, specific_prompt):
        response = await self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": specific_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }],
            response_format=InvoiceResponse,
            max_tokens=1500,
            temperature=0.0,
        )
        return response.choices[0].message.parsed

    def filter_hotel_services(self, services):
        filtered = []
        exclude = ['central gst @', 'state gst @', 'sgst @', 'cgst @', 'igst @', 'gst @', 'tax @', 'total tax', 'tax total']
        for service in services:
            if not any(pattern in service.get("description", "").lower() for pattern in exclude):
                filtered.append(service)
        return filtered

    def calculate_token_costs(self, type_prompt, data_prompt, detected_type, result_dict):
        input_tokens = (len(type_prompt) + len(data_prompt)) / 4
        output_tokens = (len(detected_type) + len(str(result_dict))) / 4
        return (input_tokens / 1000 * 0.005, output_tokens / 1000 * 0.015)

    async def process_single_image(self, image_file, type_prompt, get_prompt_by_type_func):
        try:
            image_file.seek(0)
            image_bytes = image_file.read()
            if not image_bytes:
                raise ValueError("Empty image")

            image_bytes, width, height = self.resize_image_if_needed(image_bytes)
            base64_image = self.encode_image_to_base64(image_bytes)
            image_cost = self.calculate_image_cost(width, height)

            detected_type = await self.detect_invoice_type(base64_image, type_prompt)
            data_prompt = get_prompt_by_type_func(detected_type)

            result = await self.extract_invoice_data(base64_image, data_prompt)
            result_dict = result.model_dump()
            invoice_data = result.data

            if detected_type == "hotel":
                filtered = self.filter_hotel_services(result_dict["data"]["hotel_service_breakage"])
                result_dict["data"]["hotel_service_breakage"] = filtered

            input_cost, output_cost = self.calculate_token_costs(type_prompt, data_prompt, detected_type, result_dict)

            total_cost_usd = round((image_cost * 2) + input_cost + output_cost, 6)
            total_cost_inr = round(total_cost_usd * self.usd_to_inr, 4)

            return {
                "filename": image_file.name,
                "invoice_type": detected_type,
                "structured_data": result_dict["data"],
                "estimated_cost_usd": total_cost_usd,
                "estimated_cost_inr": total_cost_inr,
                "breakdown": {
                    "image_cost_usd": round(image_cost * 2, 6),
                    "input_token_cost_usd": round(input_cost, 6),
                    "output_token_cost_usd": round(output_cost, 6),
                }
            }

        except Exception as e:
            return {
                "filename": getattr(image_file, "name", "unknown"),
                "error": str(e)
            }
