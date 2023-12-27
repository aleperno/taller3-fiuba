import PyPDF2
from io import BytesIO

def split_pdf_to_pages(pdf_reader):
  for page in range(len(pdf_reader.pages)):
    pdf_writer = PyPDF2.PdfWriter()
    pdf_writer.add_page(pdf_reader.pages[page])
    pdf_bytes = BytesIO()
    pdf_writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    pdf_reader = PyPDF2.PdfReader(stream=pdf_bytes)
    yield pdf_reader
