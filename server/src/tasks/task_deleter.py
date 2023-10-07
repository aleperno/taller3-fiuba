from src.tasks.task_repository import TaskRepository


class TaskDeleter:
    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository
    
    def delete_tasks(self):
        return self.task_repository.delete_all()
