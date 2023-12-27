from src.tasks.pdf.stored_pdf import StoredPdf
from src.tasks.pdf.stored_pdf_repository import StoredPdfRepository
from src.file_storage.file_storage import FileStorage


class PdfFileStorage:
  def __init__(self, file_storage: FileStorage, stored_pdf_repository: StoredPdfRepository):
    self.file_storage = file_storage
    self.stored_pdf_repository = stored_pdf_repository
  
  def upload(self, id, file):
    stored_file_id = self.file_storage.store(f"{id}_original.pdf", file)
    self.stored_pdf_repository.create(StoredPdf(stored_file_id))
