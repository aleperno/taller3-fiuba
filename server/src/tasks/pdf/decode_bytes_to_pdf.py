from base64 import b64decode
from io import BytesIO
import PyPDF2

def decode_bytes_to_pdf(bytes: str) -> PyPDF2.PdfReader:
  decoded_pdf_bytes = b64decode(bytes)
  pdf_object = PyPDF2.PdfReader(stream=BytesIO(decoded_pdf_bytes))
  pdf_object.stream.seek(0)
  
  return pdf_object
