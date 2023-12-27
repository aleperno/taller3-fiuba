from io import BytesIO
from base64 import b64encode
import PyPDF2

def pdf_obj_to_encoded_bytes(pdf_obj):
  pdf_writer = PyPDF2.PdfWriter()
  for page in range(len(pdf_obj.pages)):
    pdf_writer.add_page(pdf_obj.pages[page])
  
  pdf_bytes = BytesIO()
  pdf_writer.write(pdf_bytes)
  pdf_bytes.seek(0)

  encoded = b64encode(pdf_bytes.read())
  return encoded