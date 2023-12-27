from server.src.tasks.task_pdf_enqueuer import TaskPdfEnqueuer
from src.tasks.pdf.pdf_file_storage import PdfFileStorage
from src.tasks.task import Task
from src.tasks.task_data_transfer import CreateTaskRequest, TaskResponse
from src.tasks.task_repository import TaskRepository
from src.tasks.pdf.decode_bytes_to_pdf import decode_bytes_to_pdf

class TaskCreator:
    def __init__(self, task_repository: TaskRepository, pdf_file_storage: PdfFileStorage, task_pdf_enqueuer: TaskPdfEnqueuer):
        self.task_repository = task_repository
        self.pdf_file_storage = pdf_file_storage
        self.task_pdf_enqueuer = task_pdf_enqueuer

    def create_task(self, task_request: CreateTaskRequest) -> TaskResponse:
        task_pdf_file = decode_bytes_to_pdf(task_request.file_content)

        task = self.task_repository.create(Task(
            global_palette_opt=task_request.global_palette_opt,
            white_background=task_request.white_background,
            colours=task_request.colours,
            total_pages=task_request.total_pages,
            selected_pages=task_request.selected_pages
        ))

        self.pdf_file_storage.upload(task.id, task_pdf_file)
        self.task_pdf_enqueuer.enqueue(task, task_pdf_file) # TODO: Que pdf_file_storage#upload devuelva una referencia al archivo subido, y encolar eso en lugar de pasar el archivo completo

        return task
