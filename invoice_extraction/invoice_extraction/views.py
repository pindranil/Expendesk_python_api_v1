
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from invoice_extraction.process_invoice import AsyncImageProcessor
from .prompts import InvoicePrompts
import asyncio


class AnalyzeImageView(APIView):
    parser_classes = [MultiPartParser]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_processor = AsyncImageProcessor()

    def get_prompt_by_type(self, invoice_type):
        prompts = {
            'hotel': InvoicePrompts.get_hotel_prompt(),
            'travel': InvoicePrompts.get_travel_prompt(),
            'food': InvoicePrompts.get_food_prompt(),
            'other': InvoicePrompts.get_other_prompt()
        }
        return prompts.get(invoice_type.lower(), InvoicePrompts.get_other_prompt())

    def validate_image_files(self, image_files):
        validated_files = []
        errors = []

        for i, file in enumerate(image_files):
            print(f"[DEBUG] File {i+1}: {file.name}, Size: {file.size} bytes")

            if not file.name.lower().endswith((".jpg", ".jpeg", ".png")):
                errors.append({
                    "filename": file.name,
                    "error": "Unsupported file format. Only JPG/JPEG/PNG images are supported."
                })
            else:
                validated_files.append(file)

        return validated_files, errors

    async def process_images_async(self, image_files, type_detection_prompt):
        """Async processing of all validated image files"""
        tasks = [
            self.image_processor.process_single_image(file, type_detection_prompt, self.get_prompt_by_type)
            for file in image_files
        ]
        return await asyncio.gather(*tasks)
        

    def post(self, request, *args, **kwargs):
        """Handle POST request to analyze invoice images"""
        if "images" not in request.FILES:
            return Response(
                {"error": "No image files provided. Use 'images' field name."},
                status=status.HTTP_400_BAD_REQUEST
            )

        image_files = request.FILES.getlist("images")
        validated_files, validation_errors = self.validate_image_files(image_files)
        results = []
        results.extend(validation_errors)

        type_detection_prompt = InvoicePrompts.get_base_prompt()
        
        if validated_files:
            print(f"[INFO] Processing {len(validated_files)} files asynchronously")
            async_results = asyncio.run(
                self.process_images_async(validated_files, type_detection_prompt)
            )

           
            if len(async_results) == 1:
                async_results = async_results[0]


        print(f"[DEBUG] Total results: ",async_results)
        return Response(async_results, status=status.HTTP_200_OK)


