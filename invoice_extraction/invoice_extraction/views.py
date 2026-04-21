import json
import asyncio
import io

import fitz  # PyMuPDF
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from invoice_extraction.process_invoice import AsyncImageProcessor
from .prompts import InvoicePrompts


class AnalyzeImageView(APIView):
    parser_classes = [MultiPartParser]

    SUPPORTED_IMAGES = (".jpg", ".jpeg", ".png")
    SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".pdf")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_processor = AsyncImageProcessor()

    def pdf_to_images(self, pdf_file):
        """Convert each page of a PDF into a JPEG InMemoryUploadedFile."""
        pdf_bytes = pdf_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        image_files = []

        for page_index in range(len(doc)):
            page = doc[page_index]
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=95)
            buffer.seek(0)

            filename = f"{pdf_file.name}_page_{page_index + 1}.jpg"
            image_file = InMemoryUploadedFile(
                file=buffer,
                field_name="images",
                name=filename,
                content_type="image/jpeg",
                size=buffer.getbuffer().nbytes,
                charset=None,
            )
            image_files.append(image_file)
            print(f"[DEBUG] PDF page {page_index + 1} converted: {filename}")

        doc.close()
        return image_files

    def validate_files(self, uploaded_files):
        validated_jobs = []
        errors = []

        for i, file in enumerate(uploaded_files):
            lower_name = file.name.lower()
            print(f"[DEBUG] File {i+1}: {file.name}, Size: {file.size} bytes")

            if lower_name.endswith(self.SUPPORTED_IMAGES):
                validated_jobs.append(file)

            elif lower_name.endswith(".pdf"):
                try:
                    pdf_images = self.pdf_to_images(file)
                    if not pdf_images:
                        errors.append({
                            "filename": file.name,
                            "error": "PDF appears to be empty or could not be rendered."
                        })
                    else:
                        validated_jobs.append(pdf_images)
                        print(f"[INFO] PDF '{file.name}' → {len(pdf_images)} page(s) as 1 job")
                except Exception as e:
                    errors.append({
                        "filename": file.name,
                        "error": f"Failed to process PDF: {str(e)}"
                    })
            else:
                errors.append({
                    "filename": file.name,
                    "error": (
                        "Unsupported file format. "
                        "Only JPG, JPEG, PNG, and PDF files are supported."
                    )
                })

        return validated_jobs, errors

    async def process_jobs_async(self, jobs, combined_prompt, unauthorized_items):
        tasks = []
        for job in jobs:
            if isinstance(job, list):
                tasks.append(
                    self.image_processor.process_pdf_images(job, combined_prompt, unauthorized_items)
                )
            else:
                tasks.append(
                    self.image_processor.process_single_image(job, combined_prompt, unauthorized_items)
                )
        return await asyncio.gather(*tasks)

    def post(self, request, *args, **kwargs):
        """Handle POST request to analyze invoice images and PDFs."""
        if "images" not in request.FILES:
            return Response(
                {"error": "No files provided. Use 'images' field name."},
                status=status.HTTP_400_BAD_REQUEST
            )

        expense_types_raw = request.data.get("expense_types", "")
        expense_types: list[dict] = []

        if expense_types_raw:
            try:
                parsed = json.loads(expense_types_raw)
                if isinstance(parsed, list):
                    if parsed and isinstance(parsed[0], dict):
                        expense_types = parsed
                    else:
                        expense_types = [
                            {"expense_type_id": i + 1, "expense_type": name}
                            for i, name in enumerate(parsed)
                        ]
            except (json.JSONDecodeError, TypeError):
                names = [n.strip() for n in expense_types_raw.split(",") if n.strip()]
                expense_types = [
                    {"expense_type_id": i + 1, "expense_type": name}
                    for i, name in enumerate(names)
                ]

        print(f"[DEBUG] expense_types received: {expense_types}")

        unauthorized_items_raw = request.data.get("unauthorized_items", "[]")
        try:
            parsed_unauth = json.loads(unauthorized_items_raw)
            if (
                isinstance(parsed_unauth, list)
                and len(parsed_unauth) == 1
                and isinstance(parsed_unauth[0], list)
            ):
                unauthorized_items: list[dict] = parsed_unauth[0]
            else:
                unauthorized_items: list[dict] = parsed_unauth
        except (json.JSONDecodeError, TypeError):
            unauthorized_items = []
        print(f"[DEBUG] unauthorized_items received: {unauthorized_items}")

        uploaded_files = request.FILES.getlist("images")
        validated_jobs, validation_errors = self.validate_files(uploaded_files)
        results = list(validation_errors)

        combined_prompt = InvoicePrompts.get_combined_prompt(expense_types=expense_types)

        if validated_jobs:
            print(f"[INFO] Processing {len(validated_jobs)} job(s) asynchronously")
            async_results = asyncio.run(
                self.process_jobs_async(validated_jobs, combined_prompt, unauthorized_items)
            )

            if len(async_results) == 1:
                async_results = async_results[0]

            results = async_results

        print(f"[DEBUG] Total results: ", results)
        return Response(results, status=status.HTTP_200_OK)