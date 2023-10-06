from typing import List
from src.tasks.task_data_transfer import GetTaskRequest, TaskResponse
from src.tasks.task_repository import TaskRepository

class TaskGetter:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository
    
    def get_task(self, task_request: GetTaskRequest) -> TaskResponse:
        return self.task_repository.get(task_request.id)
    
    def get_tasks(self) -> List[TaskResponse]:
        return self.task_repository.get_all()