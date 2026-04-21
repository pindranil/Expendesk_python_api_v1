import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

from invoice_extraction.Image_utils    import resize_image_if_needed, encode_image_to_base64, build_image_content_blocks
from invoice_extraction.calculate_cost import calculate_image_cost, PRICING
from invoice_extraction.Ai_calls       import extract_invoice_single, extract_invoice_pdf, detect_unauthorized_items
from invoice_extraction.Result_builder import merge_unauthorized_results, build_result_dict

load_dotenv()
openai_api_key = os.getenv("OPENAI_SECRET_KEY")
if not openai_api_key:
    raise EnvironmentError("Missing OPENAI_SECRET_KEY in .env")

client = AsyncOpenAI(api_key=openai_api_key)


class AsyncImageProcessor:

    # ─────────────── Single Image ────────────────────────────────
    async def process_single_image(
        self,
        image_file,
        combined_prompt:    str,
        unauthorized_items: list[dict] | None = None,
    ) -> dict:
        unauthorized_items = unauthorized_items or []
        try:
            image_file.seek(0)
            image_bytes = image_file.read()
            if not image_bytes:
                raise ValueError("Empty image")

            image_bytes, width, height = resize_image_if_needed(image_bytes)
            base64_image = encode_image_to_base64(image_bytes)
            image_cost   = calculate_image_cost(width, height)
            image_blocks = build_image_content_blocks([base64_image])

            extra_costs: list[float] = []

            # Run main extraction + unauthorized detection concurrently
            invoice_data, unauth_results = await asyncio.gather(
                extract_invoice_single(client, base64_image, combined_prompt),
                detect_unauthorized_items(client, image_blocks, unauthorized_items, PRICING, extra_costs),
            )

            merge_unauthorized_results(invoice_data, unauth_results)

            return build_result_dict(
                invoice_data=invoice_data,
                image_file_name=image_file.name,
                combined_prompt=combined_prompt,
                total_image_cost=image_cost,
                extra_token_costs=sum(extra_costs),
            )

        except Exception as e:
            return {
                "file_name":    getattr(image_file, "name", "unknown"),
                "error":        str(e),
                "invoice_type": None,
                "status":       500,
            }

    # ─────────────── PDF (multi-page) ────────────────────────────
    async def process_pdf_images(
        self,
        image_files:        list,
        combined_prompt:    str,
        unauthorized_items: list[dict] | None = None,
    ) -> dict:
        """All pages of a single PDF sent in ONE API call. Returns a single invoice dict."""
        unauthorized_items = unauthorized_items or []
        original_name: str | None = None

        try:
            pdf_page_images: list[dict] = []
            all_base64:      list[str]  = []
            total_image_cost = 0.0

            for image_file in image_files:
                image_file.seek(0)
                image_bytes = image_file.read()
                if not image_bytes:
                    continue

                image_bytes, width, height = resize_image_if_needed(image_bytes)
                b64        = encode_image_to_base64(image_bytes)
                page_cost  = calculate_image_cost(width, height)

                pdf_page_images.append({"base64": b64, "width": width, "height": height})
                all_base64.append(b64)
                total_image_cost += page_cost

                if original_name is None:
                    original_name = image_file.name.split("_page_")[0]

            if not pdf_page_images:
                raise ValueError("No valid pages found in PDF")

            print(f"[INFO] Sending {len(pdf_page_images)} page(s) in one API call for {original_name}")

            image_blocks = build_image_content_blocks(all_base64)
            extra_costs: list[float] = []

            invoice_data, unauth_results = await asyncio.gather(
                extract_invoice_pdf(client, pdf_page_images, combined_prompt),
                detect_unauthorized_items(client, image_blocks, unauthorized_items, PRICING, extra_costs),
            )

            merge_unauthorized_results(invoice_data, unauth_results)

            return build_result_dict(
                invoice_data=invoice_data,
                image_file_name=original_name,
                combined_prompt=combined_prompt,
                total_image_cost=total_image_cost,
                extra_token_costs=sum(extra_costs),
            )

        except Exception as e:
            return {
                "file_name":    original_name or "unknown.pdf",
                "error":        str(e),
                "invoice_type": None,
                "status":       500,
            }