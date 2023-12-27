from celery import Celery
import PyPDF2

from src.tasks.pdf.split_pdf_to_pages import split_pdf_to_pages
from src.tasks.task import Task

class TaskPdfEnqueuer:
  def __init__(self, celery: Celery):
    self.celery = celery

  def enqueue(self, task: Task, pdf_reader: PyPDF2.PdfReader):
    pdf_reader.seek(0)
    pages = split_pdf_to_pages()
    for i, page in enumerate(pages):
      kw = {
        'pdf_id': str(task.id),
        'page_n': i+1,
        'pdf_bytes': pdf_obj_to_encoded_bytes(page),
        'white_background': task.white_background,
        'colour_count': task.colours,
      }
      self.celery.send_task('compress_page', kwargs=kw, queue='compression')

    return task
