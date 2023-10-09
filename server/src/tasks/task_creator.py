from celery import Celery
from src.tasks.task import Task
from src.tasks.task_data_transfer import CreateTaskRequest, TaskResponse
from src.tasks.task_repository import TaskRepository

class TaskCreator:
    def __init__(self, task_repository: TaskRepository, celery_app: Celery):
        self.task_repository = task_repository
        self.celery_app = celery_app

    def create_task(self, task_request: CreateTaskRequest) -> TaskResponse:
        task = self.task_repository.create(Task(
            global_palette_opt=task_request.global_palette_opt,
            white_background=task_request.white_background,
            colours=task_request.colours,
            total_pages=task_request.total_pages,
            selected_pages=task_request.selected_pages
        ))

        # for i in range(task.total_pages):
        #     self.celery_app.send_task('register', args=(str(task.id), i+1), queue='compression')

        return task
