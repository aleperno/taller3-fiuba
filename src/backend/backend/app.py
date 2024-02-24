import os
import time
from fastapi import FastAPI, WebSocket, HTTPException, Response, Depends, BackgroundTasks, WebSocket, WebSocketException
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware
# Para comunicarse con los workers
from celery import Celery

from .database import crud, models, SessionLocal, engine
import backend.schemas as schemas
from .database.crud import users as crud_users
from .database.crud import tasks as crud_tasks
from .utils import file_manipulation as fm
from .utils.storage import StorageHandler
from .utils.sessions import backend, cookie, SessionData, uuid4, verifier
from .utils.firebase import verify_token



models.Base.metadata.create_all(bind=engine)


origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000"
]


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


remote_celery_app = Celery()
remote_celery_app.config_from_object('backend.common.workers_celeryconfig')

local_celery_app = Celery()
local_celery_app.config_from_object('backend.common.backend_celeryconfig')


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/verify_token")
async def token_verifier(body: schemas.TokenData, response: Response, db: Session = Depends(get_db)):
    token = body.firebase_token
    decoded_token = verify_token(token)
    if decoded_token:

        session = uuid4()
        data = SessionData(user_email=decoded_token['email'])

        await backend.create(session, data)
        cookie.attach_to_response(response, session)

        email = decoded_token['email']
        name = decoded_token['name']
        user = crud_users.get_create_user_by_email(db=db, email=email, name=name)
        return user.id

    raise HTTPException(status_code=403, detail="invalid token")


async def get_user(session_data: SessionData = Depends(verifier), db: Session = Depends(get_db)):
    print(f"Busco usuario con mail {session_data.user_email}")
    user = crud_users.get_user_by_email(db=db, email=session_data.user_email)
    if not user:
        raise HTTPException(status_code=404, detail="user not found in database")
    return user


def initial_upload_task(db, user, file_id, fileb64):
    pdf_obj = fm.encoded_bytes_to_pdf_obj(fileb64)
    pdf_obj.stream.seek(0)

    crud_tasks.mark_upload_subtask_start(db, file_id)

    with StorageHandler() as handler:
        original_url = handler.upload(f"{file_id}_original.pdf", pdf_obj.stream)
        crud_tasks.set_fs_original_url(db, file_id, original_url)

    crud_tasks.mark_upload_subtask_done(db, file_id)
    local_celery_app.send_task('register_subtask_completion', queue='backend', kwargs={'file_id': file_id,
                                                                                             'subtask': 'upload_subtask'})


def schedule_compress_task(db, body, file_id, fileb64):
    pdf_obj = fm.encoded_bytes_to_pdf_obj(fileb64)
    pdf_obj.stream.seek(0)

    pages = fm.split_pdf_to_pages(pdf_obj)
    for i, page_obj in enumerate(pages):
        kw = {
            'pdf_id': file_id,
            'page_n': i+1,
            'pdf_bytes': fm.pdf_obj_to_encoded_bytes(page_obj),
            'white_background': body.white_background,
            'colour_count': body.colours,
        }
        remote_celery_app.send_task('compress_page', kwargs=kw, queue='compression')
    crud_tasks.mark_compress_subtask_start(db, file_id)


@app.post('/uploadfile', dependencies=[Depends(cookie)])
async def upload_file(body: schemas.UploadRequestSchema, background_tasks: BackgroundTasks,
                      user: models.User = Depends(get_user), db: Session=Depends(get_db)):
    file_data= crud_tasks.process_upload_request(db, user, body)

    background_tasks.add_task(initial_upload_task, db, user, file_data.id, body.file_b64)
    if body.compress:
        background_tasks.add_task(schedule_compress_task, db, body, file_data.id, body.file_b64)
    return {"content": "OK"}


@app.get('/mytasks', dependencies=[Depends(cookie)])
async def get_user_tasks(user: models.User = Depends(get_user)):
    tasks_data = crud_tasks.get_user_tasks(user)
    return tasks_data


@app.get('/myfiles', dependencies=[Depends(cookie)])
async def get_user_files(user: models.User = Depends(get_user)):
    files_data = crud_tasks.get_user_files(user)
    return files_data


@app.get('/sharedfiles', dependencies=[Depends(cookie)])
async def get_user_shared_files(user: models.User = Depends(get_user), db: Session=Depends(get_db)):
    files_data = crud_tasks.get_shared_files(user, db)
    return files_data
