from celery import Celery
from ..noteshrink.functions import shrink_pdf_bytes


app = Celery()
app.config_from_object('backend.common.workers_celeryconfig')

remote_app = Celery()
remote_app.config_from_object('backend.common.backend_celeryconfig')


@app.task(name='compress_page')
def compress_page(pdf_id, page_n, pdf_bytes, white_background=False, colour_count=5):
    print(f"Recibi la pagina {page_n} del pdf {pdf_id}")
    shrinked_bytes = shrink_pdf_bytes(pdf_bytes, white_background, colour_count)
    kw = {
        'pdf_id': pdf_id,
        'page_n': page_n,
        'encoded_bytes': shrinked_bytes
    }
    remote_app.send_task(name='register_result', kwargs=kw, queue='results')
    return 0
