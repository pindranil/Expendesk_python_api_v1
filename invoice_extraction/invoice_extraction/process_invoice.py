import io
import os
import base64
import asyncio
from PIL import Image
from dotenv import load_dotenv
from openai import AsyncOpenAI
import tiktoken
from invoice_extraction.invoice_parser import InvoiceResponse

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
        # gpt-5-mini pricing
        self.pricing = {
            "image_input": 0.00025,             # < 720x720
            "large_image_input": 0.001,         # >= 720x720
            "input_token": 0.75 / 1_000_000,    # ✅ $0.75/MTok
            "output_token": 4.50 / 1_000_000,
        }

    # ----------------- Image Utils -----------------
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
        image.save(img_byte_arr, format="JPEG", quality=75, optimize=True)
        return img_byte_arr.getvalue(), width, height

    def encode_image_to_base64(self, image_bytes):
        return base64.b64encode(image_bytes).decode("utf-8")

    def calculate_image_cost(self, width, height):
        return self.pricing["image_input"] if (width < 720 and height < 720) else self.pricing["large_image_input"]

    # ----------------- Token Utils -----------------
    def count_tokens(self, text: str):
        try:
            enc = tiktoken.encoding_for_model("gpt-5-mini")
        except KeyError:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))

    def calculate_token_costs(self, prompt, result_dict):
        input_tokens = self.count_tokens(prompt)
        output_tokens = self.count_tokens(str(result_dict))

        input_cost = input_tokens * self.pricing["input_token"]
        output_cost = output_tokens * self.pricing["output_token"]

        return input_cost, output_cost, input_tokens, output_tokens

    # ----------------- AI Call (single) -----------------
    async def extract_invoice(self, base64_image, combined_prompt):
        """Single API call — classify + extract in one shot."""
        response = await self.client.beta.chat.completions.parse(
            model="gpt-5.4-mini",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": combined_prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}",
                            "detail": "high"  # ✅ high detail for OCR accuracy
                        }
                    }
                ]
            }],
            response_format=InvoiceResponse,
            max_completion_tokens=8000,   # ✅ increased — reasoning + output both need space
            reasoning_effort="low",
        )
        return response.choices[0].message.parsed  # ✅ returns InvoiceResponse directly

    # ----------------- Helpers -----------------
    def filter_hotel_services(self, services):
        filtered = []
        exclude = [
            'central gst @', 'state gst @', 'sgst @', 'cgst @',
            'igst @', 'gst @', 'tax @', 'total tax', 'tax total'
        ]
        for service in services:
            if not any(pattern in service.get("description", "").lower() for pattern in exclude):
                filtered.append(service)
        return filtered

    # ----------------- Main Process -----------------
    async def process_single_image(self, image_file, combined_prompt):
        try:
            image_file.seek(0)
            image_bytes = image_file.read()
            if not image_bytes:
                raise ValueError("Empty image")

            # step 1: preprocess image
            image_bytes, width, height = self.resize_image_if_needed(image_bytes)
            base64_image = self.encode_image_to_base64(image_bytes)
            image_cost = self.calculate_image_cost(width, height)

            # step 2: single API call — classify + extract
            invoice_data: InvoiceResponse = await self.extract_invoice(base64_image, combined_prompt)
            detected_type = invoice_data.invoice_type.lower()
            invoice_dict = invoice_data.model_dump()

            # step 3: clean hotel services
            if detected_type == "hotel" and invoice_dict.get("hotel_service_breakage"):
                filtered_services = self.filter_hotel_services(invoice_dict["hotel_service_breakage"])
                invoice_dict["service_breakage"] = filtered_services
                invoice_dict.pop("hotel_service_breakage", None)

            # step 3b: remove discriminator `type` field
            invoice_dict.pop("type", None)

            # step 4: cost calculation
            input_cost, output_cost, input_tokens, output_tokens = self.calculate_token_costs(
                combined_prompt, invoice_dict
            )

            total_cost_usd = round(image_cost + input_cost + output_cost, 6)
            total_cost_inr = round(total_cost_usd * self.usd_to_inr, 4)

            # step 5: return response
            invoice_dict.update({
                "file_name": image_file.name,
                "invoice_type": detected_type,
                "estimated_cost_usd": total_cost_usd,
                "estimated_cost_inr": total_cost_inr,
                "image_cost_usd": round(image_cost, 6),
                "input_token_cost_usd": round(input_cost, 6),
                "output_token_cost_usd": round(output_cost, 6),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            })
            print("invoice_data:", invoice_dict)
            return invoice_dict

        except Exception as e:
            return {
                "file_name": getattr(image_file, "name", "unknown"),
                "error": str(e),
                "invoice_type": None,
                "status": 500
            }