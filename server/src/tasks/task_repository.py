from uuid import UUID
from src.tasks.task import Task

class TaskRepository:
    def __init__(self, db):
        self.db = db

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get(self, id: UUID) -> Task:
        return self.db.query(Task).filter(Task.id == id).one_or_none()

    def get_all(self) -> 'list[Task]':
        return self.db.query(Task).all()
    
    def delete_all(self):
        self.db.query(Task).delete()
        self.db.commit()
