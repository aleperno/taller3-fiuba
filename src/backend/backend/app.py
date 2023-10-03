import os
from fastapi import Depends, FastAPI, HTTPException, UploadFile
from sqlalchemy.orm import Session

# Para comunicarse con los workers
from celery import Celery

from .database import crud, models, schemas, SessionLocal, engine
from .utils import is_valid_uuid
from .utils.file_manipulation import pdfbytes_to_images

print("FastAPI intento conectar a la DB")
print(f"El usuario es {os.getuid()}")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
remote_celery_app = Celery()
remote_celery_app.config_from_object('backend.common.workers_celeryconfig')


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/compress_task/", response_model=schemas.TaskResponse)
def create_compress_task(task: schemas.TaskRequestBase, db: Session = Depends(get_db)):
    new_task = crud.create_compress_task(db=db, task=task)
    print(f"New task created! {new_task}")
    for i in range(new_task.total_pages):
        remote_celery_app.send_task('register', args=(str(new_task.id), i+1), queue='compression')
    return new_task


@app.get("/compress_task/{task_id}", response_model=schemas.TaskResponse)
def get_compress_task(task_id: str, db: Session = Depends(get_db)):
    if not is_valid_uuid(task_id):
        raise HTTPException(status_code=400, detail="Invalid UUID")
    task = crud.get_compress_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.get("/compress_task/", response_model=list[schemas.TaskResponse])
def get_all_compress_tasks(db: Session = Depends(get_db)):
    tasks = crud.get_all_compress_task(db)
    return tasks


@app.post("/uploadfile/")
def create_upload_file(file_content: schemas.ImageUpload):
    converted_images = pdfbytes_to_images(file_content.file_content)
    if not converted_images:
        raise HTTPException(status_code=400, detail="Invalid PDF")

    files = []

    for n, image in enumerate(converted_images):
        image.save(f"/tmp/test_{n}.png")
        files.append(f"/tmp/test_{n}.png")

    return {"content": files}
