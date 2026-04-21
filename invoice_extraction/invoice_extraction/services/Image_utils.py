import io
import base64
from PIL import Image


def resize_image_if_needed(image_bytes: bytes, max_dimension: int = 1024) -> tuple[bytes, int, int]:
    """Resize image to max_dimension if either side exceeds it. Returns (bytes, width, height)."""
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


def encode_image_to_base64(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def build_image_content_blocks(base64_images: list[str]) -> list[dict]:
    """Return OpenAI-style image_url content blocks for each base64 image."""
    return [
        {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{b64}",
                "detail": "high"
            }
        }
        for b64 in base64_images
    ]