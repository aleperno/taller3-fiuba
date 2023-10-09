from typing import List
from fastapi import FastAPI, Depends
from celery import Celery

from src.database import get_session

from src.tasks.task_creator import TaskCreator
from src.tasks.task_getter import TaskGetter
from src.tasks.task_deleter import TaskDeleter
from src.tasks.task_repository import TaskRepository
from src.tasks.task_data_transfer import CreateTaskRequest, TaskResponse, TaskRequest

app = FastAPI()

def get_celery():
    celery = Celery()
    celery.config_from_object('src.celery_config')
    yield celery

def get_task_repository(db_session = Depends(get_session)):
    yield TaskRepository(db_session)

def task_creator(task_repository = Depends(get_task_repository), celery = Depends(get_celery)) -> TaskCreator:
    yield TaskCreator(task_repository, celery)

def task_getter(task_repository = Depends(get_task_repository)) -> TaskGetter:
    yield TaskGetter(task_repository)

def task_deleter(task_repository = Depends(get_task_repository)) -> TaskDeleter:
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