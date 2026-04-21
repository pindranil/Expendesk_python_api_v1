import json
import asyncio
import io
import threading
import time

import fitz  # PyMuPDF
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from invoice_extraction.process_invoice import AsyncImageProcessor
from invoice_extraction.prompts import InvoicePrompts

# ─────────────────────────────────────────────────────────────
# Tuneable constants
# ─────────────────────────────────────────────────────────────
MAX_CONCURRENT_JOBS = 3      # max parallel Anthropic API calls at one time
REQUEST_TIMEOUT_SEC = 120    # per-attempt timeout (seconds) — increased from 90
MAX_RETRIES = 5              # how many times to retry on connection error — increased from 3
RETRY_BASE_DELAY = 3.0       # seconds; doubles on each retry (3s, 6s, 12s, 24s)


def run_async_in_thread(coro):

    result_container = []
    exception_container = []

    def thread_target():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result_container.append(loop.run_until_complete(coro))
        except Exception as e:
            exception_container.append(e)
        finally:
            loop.close()

    t = threading.Thread(target=thread_target)
    t.start()
    t.join()

    if exception_container:
        raise exception_container[0]
    return result_container[0]


class AnalyzeImageView(APIView):
    parser_classes = [MultiPartParser]

    SUPPORTED_IMAGES = (".jpg", ".jpeg", ".png", ".jpeg")
    SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".pdf", ".jpeg")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_processor = AsyncImageProcessor()

    # ──────────────────────────────────────────
    # PDF → list[InMemoryUploadedFile]
    # ──────────────────────────────────────────
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

    # ──────────────────────────────────────────
    # File validation
    # ──────────────────────────────────────────
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

    # ──────────────────────────────────────────
    # Retry wrapper
    # ──────────────────────────────────────────
    async def _with_retry(self, coro_fn, file_name: str):

        last_error = None

        for attempt in range(1, MAX_RETRIES + 1):
            attempt_start = time.time()
            print(f"[DEBUG] '{file_name}' — attempt {attempt}/{MAX_RETRIES} starting "
                  f"(timeout={REQUEST_TIMEOUT_SEC}s)")
            try:
                result = await asyncio.wait_for(coro_fn(), timeout=REQUEST_TIMEOUT_SEC)
                elapsed = time.time() - attempt_start
                print(f"[DEBUG] '{file_name}' — attempt {attempt} SUCCEEDED in {elapsed:.1f}s")
                if attempt > 1:
                    print(f"[INFO] '{file_name}' succeeded on attempt {attempt}")
                return result

            except asyncio.TimeoutError:
                elapsed = time.time() - attempt_start
                last_error = f"Request timed out after {elapsed:.1f}s."
                print(f"[WARN] '{file_name}' TIMED OUT on attempt {attempt}/{MAX_RETRIES} "
                      f"after {elapsed:.1f}s")

            except Exception as e:
                elapsed = time.time() - attempt_start
                last_error = str(e)
                print(f"[WARN] '{file_name}' ERROR on attempt {attempt}/{MAX_RETRIES} "
                      f"after {elapsed:.1f}s — {type(e).__name__}: {e}")

            if attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))  # 3s, 6s, 12s, 24s
                print(f"[INFO] Retrying '{file_name}' in {delay:.1f}s ... "
                      f"(attempt {attempt + 1}/{MAX_RETRIES})")
                await asyncio.sleep(delay)

        # All retries exhausted
        print(f"[ERROR] ============================================================")
        print(f"[ERROR] '{file_name}' FAILED after {MAX_RETRIES} attempts.")
        print(f"[ERROR] Final error: {repr(last_error)}")
        print(f"[ERROR] ============================================================")
        return {
            "file_name": file_name,
            "error": last_error or "Connection error.",
            "invoice_type": None,
            "status": 500,
        }

    # ──────────────────────────────────────────
    # Async job runner with semaphore + retry
    # ──────────────────────────────────────────
    async def process_jobs_async(self, jobs, combined_prompt, unauthorized_items):

        semaphore = asyncio.Semaphore(MAX_CONCURRENT_JOBS)

        async def run_job(job):
            if isinstance(job, list):
                job_name = job[0].name if job else "unknown_pdf"
            else:
                job_name = job.name

            print(f"[DEBUG] Job queued: '{job_name}' — waiting for semaphore slot...")
            async with semaphore:
                print(f"[DEBUG] Job started: '{job_name}' — semaphore acquired")
                start = time.time()

                if isinstance(job, list):
                    # IMPORTANT: use default arg (j=job) to capture loop variable correctly
                    result = await self._with_retry(
                        lambda j=job: self.image_processor.process_pdf_images(
                            j, combined_prompt, unauthorized_items
                        ),
                        file_name=job_name,
                    )
                else:
                    # IMPORTANT: use default arg (f=job) to capture loop variable correctly
                    result = await self._with_retry(
                        lambda f=job: self.image_processor.process_single_image(
                            f, combined_prompt, unauthorized_items
                        ),
                        file_name=job_name,
                    )

                elapsed = time.time() - start
                print(f"[DEBUG] Job finished: '{job_name}' in {elapsed:.1f}s — "
                      f"result keys: {list(result.keys()) if isinstance(result, dict) else 'list'}")
                return result

        print(f"[INFO] Processing {len(jobs)} job(s) asynchronously "
              f"(max {MAX_CONCURRENT_JOBS} concurrent, timeout={REQUEST_TIMEOUT_SEC}s, "
              f"retries={MAX_RETRIES})")
        return await asyncio.gather(*[run_job(job) for job in jobs])

    # ──────────────────────────────────────────
    # POST handler
    # ──────────────────────────────────────────
    def post(self, request, *args, **kwargs):
        """Handle POST request to analyze invoice images and PDFs."""
        request_start = time.time()
        print(f"[DEBUG] ========== NEW REQUEST ==========")

        if "images" not in request.FILES:
            return Response(
                {"error": "No files provided. Use 'images' field name."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ── Parse expense_types ──────────────────
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

        # ── Parse unauthorized_items ─────────────
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

        # ── Validate uploaded files ──────────────
        uploaded_files = request.FILES.getlist("images")
        print(f"[DEBUG] Total files received: {len(uploaded_files)}")
        validated_jobs, validation_errors = self.validate_files(uploaded_files)
        print(f"[DEBUG] Validated jobs: {len(validated_jobs)}, Validation errors: {len(validation_errors)}")

        combined_prompt = InvoicePrompts.get_combined_prompt(expense_types=expense_types)

        # ── Run async processing ─────────────────
        async_results = []
        if validated_jobs:
            print(f"[INFO] Processing {len(validated_jobs)} job(s) asynchronously")
            processing_start = time.time()

            # Use run_async_in_thread instead of asyncio.run() to avoid
            # event loop conflicts when Django handles concurrent requests.
            raw = run_async_in_thread(
                self.process_jobs_async(validated_jobs, combined_prompt, unauthorized_items)
            )

            processing_elapsed = time.time() - processing_start
            print(f"[DEBUG] Async processing completed in {processing_elapsed:.1f}s")
            print(f"[DEBUG] Raw results count: {len(raw)}, types: {[type(r).__name__ for r in raw]}")

            async_results = []
            for i, item in enumerate(raw):
                if isinstance(item, list):
                    print(f"[DEBUG] Result[{i}] is a list (PDF) with {len(item)} page(s) — flattening")
                    async_results.extend(item)
                elif isinstance(item, dict):
                    # Log whether this is a success or error result
                    if "error" in item and item["error"]:
                        print(f"[DEBUG] Result[{i}] is an ERROR dict: "
                              f"file='{item.get('file_name')}', error='{item.get('error')}'")
                    else:
                        print(f"[DEBUG] Result[{i}] is a SUCCESS dict: "
                              f"file='{item.get('file_name')}', type='{item.get('invoice_type')}'")
                    async_results.append(item)
                else:
                    print(f"[WARN] Result[{i}] is unexpected type {type(item).__name__}: {item}")
                    async_results.append(item)

        # Merge validation errors + async results into one flat list
        results = list(validation_errors) + async_results

        total_elapsed = time.time() - request_start
        print(f"[DEBUG] Total results: {len(results)}")
        print(f"[DEBUG] Total request time: {total_elapsed:.1f}s")
        print(f"[DEBUG] Response size estimate: ~{sum(len(str(r)) for r in results)} chars")
        print(f"[DEBUG] ========== REQUEST COMPLETE ==========")

        return Response(results, status=status.HTTP_200_OK)