import asyncio
import time

from invoice_extraction.utility_function.constants import (
    MAX_RETRIES, REQUEST_TIMEOUT_SEC, RETRY_BASE_DELAY, MAX_CONCURRENT_AI_CALLS
)
from invoice_extraction.process_invoice import AsyncImageProcessor

# Global semaphore — caps concurrent AI API calls
_ai_semaphore = asyncio.Semaphore(MAX_CONCURRENT_AI_CALLS)


async def with_retry(coro_fn, file_name: str, request_id: str):
    """Retry wrapper with exponential back-off."""
    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        attempt_start = time.time()
        print(f"[{request_id}] '{file_name}' — attempt {attempt}/{MAX_RETRIES} "
              f"(timeout={REQUEST_TIMEOUT_SEC}s)")
        try:
            result  = await asyncio.wait_for(coro_fn(), timeout=REQUEST_TIMEOUT_SEC)
            elapsed = time.time() - attempt_start
            print(f"[{request_id}] '{file_name}' — attempt {attempt} succeeded in {elapsed:.1f}s")
            return result

        except asyncio.TimeoutError:
            elapsed    = time.time() - attempt_start
            last_error = f"Request timed out after {elapsed:.1f}s."
            print(f"[{request_id}] '{file_name}' TIMED OUT on attempt {attempt}/{MAX_RETRIES}")

        except Exception as e:
            elapsed    = time.time() - attempt_start
            last_error = str(e)
            print(f"[{request_id}] '{file_name}' ERROR on attempt {attempt}/{MAX_RETRIES} "
                  f"— {type(e).__name__}: {e}")

        if attempt < MAX_RETRIES:
            delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))   # 3s, 6s, 12s, 24s
            print(f"[{request_id}] Retrying '{file_name}' in {delay:.1f}s …")
            await asyncio.sleep(delay)

    print(f"[{request_id}] '{file_name}' FAILED after {MAX_RETRIES} attempts.")
    return {
        "file_name":    file_name,
        "error":        last_error or "Connection error.",
        "invoice_type": None,
        "status":       500,
    }


async def process_job(job, combined_prompt, unauthorized_items, request_id: str):
    """Run one job through the AI processor with semaphore and retry."""
    image_processor = AsyncImageProcessor()

    try:
        async with _ai_semaphore:
            if isinstance(job, list):
                job_name = job[0].name if job else "unknown_pdf"
                result = await with_retry(
                    lambda j=job: image_processor.process_pdf_images(
                        j, combined_prompt, unauthorized_items
                    ),
                    file_name=job_name,
                    request_id=request_id,
                )
            else:
                job_name = job.name
                result = await with_retry(
                    lambda f=job: image_processor.process_single_image(
                        f, combined_prompt, unauthorized_items
                    ),
                    file_name=job_name,
                    request_id=request_id,
                )
    finally:
        if hasattr(image_processor, "aclose"):
            try:
                await image_processor.aclose()
            except Exception:
                pass
        elif hasattr(image_processor, "close"):
            try:
                result_close = image_processor.close()
                if asyncio.iscoroutine(result_close):
                    await result_close
            except Exception:
                pass

    return result