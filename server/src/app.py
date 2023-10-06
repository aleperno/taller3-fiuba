from typing import List
from fastapi import FastAPI, Depends
from celery import Celery

from src.database import get_session

from src.tasks.task_creator import TaskCreator
from src.tasks.task_getter import TaskGetter
from src.tasks.task_repository import TaskRepository
from src.tasks.task_data_transfer import CreateTaskRequest, TaskResponse, GetTaskRequest

app = FastAPI()

db_session = get_session()
task_repository = TaskRepository(db_session)
celery = Celery()
celery.config_from_object('backend.common.workers_celeryconfig')

def task_creator() -> TaskCreator:
    return TaskCreator(task_repository, celery)

def task_getter() -> TaskGetter:
    return TaskGetter(task_repository)
    

@app.post("/tasks/compress", response_model=TaskResponse)
def create_compress_task(task: CreateTaskRequest, task_creator: TaskCreator = Depends(task_creator)):
    return task_creator.create_task(task)

@app.get("tasks/compress/{task_id}", response_model=TaskResponse)
def get_compress_task(task: GetTaskRequest, task_getter = Depends(task_getter)):
    return task_getter.get_task(task)

@app.get("tasks/compress", response_model=List[TaskResponse])
def get_tasks(task_getter = Depends(task_getter)):
    return task_getter.get_tasks()
