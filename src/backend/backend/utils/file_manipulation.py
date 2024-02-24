import base64

from magic import from_buffer
from pdf2image import convert_from_bytes
from PIL import Image
from io import BytesIO
from base64 import b64encode, b64decode
import PyPDF2
from typing import Optional, List


def pdf_obj_to_images(pdf_obj):
    try:
        encoded = pdf_obj_to_encoded_bytes(pdf_obj)
        _bytes = base64.b64decode(encoded)
        return convert_from_bytes(_bytes)
    except:
        return None


def validate_pdf_bytes(encoded_bytes: str) -> int:
    try:
        pdf_obj = encoded_bytes_to_pdf_obj(encoded_bytes)
        return len(pdf_obj.pages)
    except:
        return None


def split_pdf_to_pages(pdf_obj):
    for page in range(len(pdf_obj.pages)):
        pdf_writer = PyPDF2.PdfWriter()
        pdf_writer.add_page(pdf_obj.pages[page])
        pdf_bytes = BytesIO()
        pdf_writer.write(pdf_bytes)
        pdf_bytes.seek(0)

        pdf_reader = PyPDF2.PdfReader(stream=pdf_bytes)

        yield pdf_reader


def merge_pdf_pages(pdf_pages):
    pdf_writer = PyPDF2.PdfWriter()
    for page in pdf_pages:
        for subpage in page.pages:
            pdf_writer.add_page(subpage)

    pdf_bytes = BytesIO()
    pdf_writer.write(pdf_bytes)
    pdf_bytes.seek(0)
    pdf_reader = PyPDF2.PdfReader(stream=pdf_bytes)

    return pdf_reader


def encoded_bytes_to_pdf_obj(encoded_bytes: str) -> PyPDF2.PdfFileReader:
    """
    Reads a PDF File from a b64 encoded bytes and returns a PyPDF2.PdfFileReader object
    """
    try:
        decoded = b64decode(encoded_bytes)
        pdf_obj = PyPDF2.PdfReader(stream=BytesIO(decoded))
        return pdf_obj
    except Exception as e:
        return None


def pdf_obj_to_encoded_bytes(pdf_obj) -> str:
    """
    Reads a PDF File from a PyPDF2.PdfFileReader object and returns the file contents
    as b64 encoded bytes
    """
    pdf_writer = PyPDF2.PdfWriter()
    for page in range(len(pdf_obj.pages)):
        pdf_writer.add_page(pdf_obj.pages[page])

    pdf_bytes = BytesIO()
    pdf_writer.write(pdf_bytes)
    pdf_bytes.seek(0)

    encoded = base64.b64encode(pdf_bytes.read())
    return encoded


def path_to_pdf_obj(path: str) -> PyPDF2.PdfFileReader:
    try:
        pdf_writer = PyPDF2.PdfWriter()
        with open(path, 'rb') as file_obj:
            pdf_reader = PyPDF2.PdfReader(file_obj)
            for page in pdf_reader.pages:
                pdf_writer.add_page(page)

        pdf_bytes = BytesIO()
        pdf_writer.write(pdf_bytes)
        return PyPDF2.PdfReader(stream=pdf_bytes)

    except Exception as e:
        return None


def pdf_obj_to_path(pdf_obj, path):
    pdf_writer = PyPDF2.PdfWriter()
    for page in range(len(pdf_obj.pages)):
        pdf_writer.add_page(pdf_obj.pages[page])

    with open(path, 'wb') as file_obj:
        pdf_writer.write(file_obj)
