from itertools import chain
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from backend.database import models
from backend import schemas


OPTION_MODEL_MAPPER = {
    'compress': [models.CompressSubTask],
    'convert_latex': [models.LatexConvertSubTask, models.LatexBuildSubTask]
}

SUBTASK_OPTIONS_MAPPER = {
    'compress': ['colours', 'white_background']
}


def process_upload_request(db: Session, user: models.User, request: schemas.UploadRequestSchema):
    file_data = models.FileData(user_id=user.id,
                                file_name=request.file_name,
                                page_count=request.page_count,
                                privacy=request.privacy)

    db.add(file_data)
    db.commit()
    db.refresh(file_data)

    for email in request.shared_emails:
        shared_model = models.SharedData(file_id=file_data.id,
                                         email=email)
        db.add(shared_model)

    file_storage = models.FileStorage(file_id=file_data.id)
    db.add(file_storage)

    note_task = models.NoteTask(file_id=file_data.id,
                                compress=request.compress,
                                convert=request.convert_latex)

    db.add(note_task)
    db.commit()
    db.refresh(note_task)

    upload_task = models.UploadSubTask(note_task_id=note_task.id)
    db.add(upload_task)

    # Check for optional tasks
    for option, task_models in OPTION_MODEL_MAPPER.items():
        request_dict = dict(request)
        if request_dict.get(option):
            for task_model in task_models:
                base_data = {'note_task_id': note_task.id}
                if option in SUBTASK_OPTIONS_MAPPER:
                    base_data.update({suboption: request_dict.get(suboption) for suboption in SUBTASK_OPTIONS_MAPPER[option]})

                task = task_model(**base_data)
                db.add(task)

    db.commit()

    return file_data


def mark_upload_subtask_start(db: Session, file_id: str):
    file = db.query(models.FileData).filter(models.FileData.id == file_id).one()
    #db.merge(file)
    note_task = file.note_task
    note_task.current_process = models.NoteTaskCurrentProcessEnum.uploading
    note_task.status = models.BaseTaskStateEnum.in_progress

    upload_subtask = note_task.upload_subtask
    upload_subtask.status = models.BaseTaskStateEnum.in_progress
    #db.add(file)
    db.commit()


def mark_compress_subtask_start(db: Session, file_id: str):
    file = db.query(models.FileData).filter(models.FileData.id == file_id).one()
    #db.merge(file)
    note_task = file.note_task
    #note_task.current_process = models.NoteTaskCurrentProcessEnum.uploading
    note_task.status = models.BaseTaskStateEnum.in_progress

    flag_modified(note_task, 'last_updated')

    compress_subtask = note_task.compress_subtask
    compress_subtask.status = models.BaseTaskStateEnum.in_progress
    #db.add(file)
    db.commit()


def mark_upload_subtask_done(db: Session, file_id: str):
    file = db.query(models.FileData).filter(models.FileData.id == file_id).one()

    note_task = file.note_task

    upload_subtask = note_task.upload_subtask
    upload_subtask.status = models.BaseTaskStateEnum.done
    upload_subtask.progress = 100

    flag_modified(note_task, 'last_updated')

    db.commit()


def set_fs_original_url(db: Session, file_id: str, file_url: str):
    file_storage = db.query(models.FileStorage).filter(models.FileStorage.file_id == file_id).one()
    file_storage.original_url = file_url
    db.commit()


def get_user_tasks(user: models.User):
    SUBTASK_MAPPING = {
        'upload': 'upload_subtask',
        'compress': 'compress_subtask',
        'convert_latex': 'latex_convert_subtask',
        'build_latex': 'latex_build_subtask'
    }
    result = {}
    for file_data in user.file_data:
        file_result = {
            'file_name': file_data.file_name,
        }

        nt = file_data.note_task
        file_result.update({
            'status': nt.status.value,
            'created_at': nt.created_at,
            'last_updated': nt.last_updated,
        })

        for option, subtask in SUBTASK_MAPPING.items():
            subtask = getattr(nt, subtask, None)
            if subtask:
                file_result[option] = {
                    'progress': subtask.progress,
                    'status': subtask.status.value,
                    'created_at': subtask.created_at,
                    'last_updated': subtask.last_updated,
                }
        result[file_data.id] = file_result
    return result


def get_user_files(user: models.User):
    result = {}
    storage_opts = ('original_url', 'compressed_url', 'latex_zip_url', 'latex_pdf_url')
    for file_data in user.file_data:
        data = {
            'file_name': file_data.file_name,
            'created_at': file_data.created_at,
            'last_updated': file_data.note_task.last_updated,
            'privacy': file_data.privacy.value,
            'shared_with': ', '.join(shared.email for shared in file_data.shared_data)
        }
        data.update({opt: getattr(file_data.file_storage, opt) for opt in storage_opts})
        result[file_data.id] = data
    return result


def get_shared_files(user: models.User, db: Session):
    result = {}
    storage_opts = ('original_url', 'compressed_url', 'latex_zip_url', 'latex_pdf_url')
    # Primero obtengo todos los archivos que son publicos
    public_files = db.query(models.FileData).filter(models.FileData.privacy == models.FilePrivacyEnum.public).all()

    # Luego obtengo todos los archivos que me fueron compartidos
    _shared_files = db.query(models.SharedData).filter(models.SharedData.email == user.email).all()
    shared_files = [sf.file for sf in _shared_files]

    for file_data in chain(shared_files, public_files):
        owner = file_data.user
        if owner == user:
            continue
        data = {
            'owner_name': owner.name,
            'owner_email': owner.email,
            'file_name': file_data.file_name,
            'created_at': file_data.created_at,
            'last_updated': file_data.note_task.last_updated,
            'privacy': file_data.privacy.value,
        }
        data.update({opt: getattr(file_data.file_storage, opt) for opt in storage_opts})
        result[file_data.id] = data
    return result
