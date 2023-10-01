from celery import Celery
from sqlalchemy.orm.exc import StaleDataError

from ..database import SessionLocal
from ..database.models import CompressTask
import time

app = Celery()
app.config_from_object('backend.common.backend_celeryconfig')

S = SessionLocal()


@app.task(name='register_result')
def register_result(pdf_id, page_n):
    #time.sleep(10)
    print(f"Recibi el resultado de la pagina {page_n} del pdf {pdf_id}")
    try:
        with S.begin():
            #task = S.query(CompressTask).with_for_update(of=CompressTask).filter_by(id=pdf_id).first()
            task = S.query(CompressTask).with_for_update(of=CompressTask).filter_by(id=pdf_id).first()
            if task:
                task.pages_done += 1
                S.commit()
                print(f"Task {pdf_id} updated")
            else:
                print(f"Task {pdf_id} not found")
    except StaleDataError:
        print("Another worker modified the row before this worker could lock it.")
