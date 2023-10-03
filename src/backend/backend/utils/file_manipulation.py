from magic import from_buffer
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO
from base64 import b64encode, b64decode
from typing import Optional, List


def pdf_to_images(pdf_bytes):
    return convert_from_bytes(pdf_bytes)


def pdfbytes_to_images(b64pdf_bytes: str):
    try:
        decoded = b64decode(b64pdf_bytes)
        print(decoded)
        filetype = from_buffer(decoded, mime=True)
        print(filetype)
        if filetype == 'application/pdf':
            return pdf_to_images(decoded)
    except Exception as e:
        print(f"Algo paso {e}")
        return None


def image_to_b64(image) -> str:
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return b64encode(buffered.getvalue())


def b64_to_image(b64: str):
    try:
        return Image.open(BytesIO(b64decode(b64)))
    except:
        return None
