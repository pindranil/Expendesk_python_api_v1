import json
import time

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from invoice_extraction.utility_function.services import process_job
from invoice_extraction.utility_function.validators import validate_file
from invoice_extraction.prompts import InvoicePrompts


class AnalyzeImageView(APIView):
    parser_classes = [MultiPartParser]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if iscoroutinefunction(cls.post):
            markcoroutinefunction(cls)

    def initialize_request(self, request, *args, **kwargs):
        return super().initialize_request(request, *args, **kwargs)

    async def dispatch(self, request, *args, **kwargs):
        self.args    = args
        self.kwargs  = kwargs
        request      = self.initialize_request(request, *args, **kwargs)
        self.request = request
        self.headers = self.default_response_headers

        try:
            self.initial(request, *args, **kwargs)
            handler = (
                getattr(self, request.method.lower(), self.http_method_not_allowed)
                if request.method.lower() in self.http_method_names
                else self.http_method_not_allowed
            )
            response = await handler(request, *args, **kwargs)
        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response

    async def post(self, request, *args, **kwargs):
        request_start = time.time()
        request_id    = request.headers.get("X-Request-ID", "no-request-id")
        print(f"[{request_id}] ===== NEW REQUEST =====")

        if "images" not in request.FILES:
            return Response(
                {"error": "No files provided. Use 'images' field name."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        uploaded_files = request.FILES.getlist("images")

        if len(uploaded_files) != 1:
            print(f"[{request_id}] WARNING: expected 1 file, got {len(uploaded_files)}")

        # ── Parse expense_types ──────────────────────────────────────────────
        expense_types = _parse_expense_types(request.data.get("expense_types", ""))
        print(f"[{request_id}] expense_types: {expense_types}")

        # ── Parse unauthorized_items ─────────────────────────────────────────
        unauthorized_items = _parse_unauthorized_items(
            request.data.get("unauthorized_items", "[]")
        )
        print(f"[{request_id}] unauthorized_items: {unauthorized_items}")

        # ── Validate file ────────────────────────────────────────────────────
        file = uploaded_files[0]
        job, validation_error = await validate_file(file, request_id)

        if validation_error:
            print(f"[{request_id}] Validation failed: {validation_error['error']}")
            return Response([validation_error], status=status.HTTP_200_OK)

        # ── Process ──────────────────────────────────────────────────────────
        combined_prompt  = InvoicePrompts.get_combined_prompt(expense_types=expense_types)
        processing_start = time.time()

        result = await process_job(job, combined_prompt, unauthorized_items, request_id)

        processing_elapsed = time.time() - processing_start
        results            = result if isinstance(result, list) else [result]
        total_elapsed      = time.time() - request_start

        print(f"[{request_id}] Done in {processing_elapsed:.1f}s "
              f"(total {total_elapsed:.1f}s) → {len(results)} result(s)")
        print(f"[{request_id}] ===== REQUEST COMPLETE =====")

        return Response(results, status=status.HTTP_200_OK)


# ── Private parse helpers ────────────────────────────────────────────────────

def _parse_expense_types(raw: str) -> list[dict]:
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return (
                parsed if parsed and isinstance(parsed[0], dict)
                else [
                    {"expense_type_id": i + 1, "expense_type": name}
                    for i, name in enumerate(parsed)
                ]
            )
    except (json.JSONDecodeError, TypeError):
        pass
    names = [n.strip() for n in raw.split(",") if n.strip()]
    return [{"expense_type_id": i + 1, "expense_type": name} for i, name in enumerate(names)]


def _parse_unauthorized_items(raw: str) -> list[dict]:
    try:
        parsed = json.loads(raw)
        if (
            isinstance(parsed, list)
            and len(parsed) == 1
            and isinstance(parsed[0], list)
        ):
            return parsed[0]
        return parsed
    except (json.JSONDecodeError, TypeError):
        return []