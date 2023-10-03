from sqlalchemy.orm import Session

from . import models, schemas


def get_compress_task(db: Session, task_id: str):
    return db.query(models.CompressTask).filter(models.CompressTask.id == task_id).one_or_none()


def get_all_compress_task(db: Session):
    return db.query(models.CompressTask).all()


def create_compress_task(db: Session, task: schemas.TaskRequestBase):
    compress_task = models.CompressTask(global_palette_opt=task.global_palette_opt,
                                        white_background=task.white_background,
                                        colours=task.colours, total_pages=task.total_pages,
                                        selected_pages=task.selected_pages)
    db.add(compress_task)
    db.commit()
    db.refresh(compress_task)
    return compress_task
