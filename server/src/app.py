from typing import List
from fastapi import FastAPI, Depends
from celery import Celery

from src.database import Base, get_session, engine

from src.tasks.task_creator import TaskCreator
from src.tasks.task_getter import TaskGetter
from src.tasks.task_deleter import TaskDeleter
from src.tasks.task_repository import TaskRepository
from src.tasks.task_data_transfer import CreateTaskRequest, TaskResponse, TaskRequest

app = FastAPI()

Base.metadata.create_all(bind=engine)

db_session = get_session()
task_repository = TaskRepository(db_session)
celery = Celery()
celery.config_from_object('backend.common.workers_celeryconfig')

def task_creator() -> TaskCreator:
    yield TaskCreator(task_repository, celery)

def task_getter() -> TaskGetter:
    yield TaskGetter(task_repository)

def task_deleter() -> TaskDeleter:
    yield TaskDeleter(task_repository)
    

@app.post("/tasks/compress", response_model=TaskResponse)
def create_compress_task(task: CreateTaskRequest, task_creator: TaskCreator = Depends(task_creator)):
    return task_creator.create_task(task)

@app.get("/tasks/compress/{task_id}", response_model=TaskResponse)
def get_compress_task(task: TaskRequest, task_getter = Depends(task_getter)):
    return task_getter.get_task(task.id)

@app.get("/tasks/compress", response_model=List[TaskResponse])
def get_compress_tasks(task_getter = Depends(task_getter)):
    return task_getter.get_tasks()

@app.delete("/tasks/compress")
def delete_compress_tasks(task_deleter = Depends(task_deleter)):
    return task_deleter.delete_tasks()