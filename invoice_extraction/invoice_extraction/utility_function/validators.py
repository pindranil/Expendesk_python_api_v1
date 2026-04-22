import asyncio
import io
import fitz
from PIL import Image
from django.core.files.uploadedfile import InMemoryUploadedFile


SUPPORTED_IMAGES  = (".jpg", ".jpeg", ".png")
SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".pdf")


def pdf_to_images(pdf_file, request_id: str):
    """Sync — called via asyncio.to_thread() so it never blocks the event loop."""
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    image_files = []

    for page_index in range(len(doc)):
        page = doc[page_index]
        mat  = fitz.Matrix(2.0, 2.0)
        pix  = page.get_pixmap(matrix=mat, alpha=False)

        img    = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=95)
        buffer.seek(0)

        filename   = f"{pdf_file.name}_page_{page_index + 1}.jpg"
        image_file = InMemoryUploadedFile(
            file=buffer,
            field_name="images",
            name=filename,
            content_type="image/jpeg",
            size=buffer.getbuffer().nbytes,
            charset=None,
        )
        image_files.append(image_file)
        print(f"[{request_id}] PDF page {page_index + 1} converted: {filename}")

    doc.close()
    return image_files


async def validate_file(file, request_id: str):
    """Validate and normalise a single uploaded file."""
    lower_name = file.name.lower()
    print(f"[{request_id}] Validating: {file.name}  ({file.size} bytes)")

    if lower_name.endswith(SUPPORTED_IMAGES):
        return file, None

    if lower_name.endswith(".pdf"):
        try:
            pdf_images = await asyncio.to_thread(pdf_to_images, file, request_id)
            if not pdf_images:
                return None, {
                    "filename": file.name,
                    "error": "PDF appears to be empty or could not be rendered.",
                }
            print(f"[{request_id}] PDF '{file.name}' → {len(pdf_images)} page(s)")
            return pdf_images, None
        except Exception as e:
            return None, {"filename": file.name, "error": f"Failed to process PDF: {e}"}

    return None, {
        "filename": file.name,
        "error": "Unsupported file format. Only JPG, JPEG, PNG, and PDF are supported.",
    }