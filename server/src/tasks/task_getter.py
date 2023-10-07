from typing import List
import uuid
from src.tasks.task_data_transfer import TaskResponse
from src.tasks.task_repository import TaskRepository

class TaskGetter:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository
    
    def get_task(self, task_id: uuid) -> TaskResponse:
        return self.task_repository.get(task_id)
    
    def get_tasks(self) -> List[TaskResponse]:
        return self.task_repository.get_all()