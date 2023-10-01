from celery import Celery
from ..common.constants import RABBIT_HOST

#RABBIT_HOST="localhost"

app = Celery()
app.config_from_object('backend.common.workers_celeryconfig')

remote_app = Celery()
remote_app.config_from_object('backend.common.backend_celeryconfig')


@app.task(name='register')
def register(pdf_id, page_n):
    print(f"Recibi la pagina {page_n} del pdf {pdf_id}")
    remote_app.send_task(name='register_result', args=(pdf_id, page_n), queue='results')
    return 0
