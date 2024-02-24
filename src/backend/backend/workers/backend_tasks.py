from celery import Celery
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import and_, or_

from ..database import SessionLocal
from ..database import models
from ..utils import file_manipulation as fm
from ..utils import mathpix
from ..utils.storage import StorageHandler
import copy
import os
import shutil

app = Celery()
app.config_from_object('backend.common.backend_celeryconfig')

S = SessionLocal()


def get_file_path(pdf_id, page_n):
    if not os.path.exists(f"/tmp/{pdf_id}"):
        os.mkdir(f"/tmp/{pdf_id}")
    return f"/tmp/{pdf_id}/{pdf_id}_{page_n}.pdf"


def process_pdf_obj(pdf_id, page_n, encoded_bytes):
    pdf_obj = fm.encoded_bytes_to_pdf_obj(encoded_bytes)
    file_path = get_file_path(pdf_id, page_n)
    fm.pdf_obj_to_path(pdf_obj, file_path)


def merge_and_save(pdf_id, total_pages):
    pdf_obj_list = []
    for i in range(total_pages):
        page_n = i+1
        file_path = get_file_path(pdf_id, page_n)
        pdf_obj = fm.path_to_pdf_obj(file_path)
        pdf_obj_list.append(pdf_obj)

    merged_pdf_obj = fm.merge_pdf_pages(pdf_obj_list)
    fm.pdf_obj_to_path(merged_pdf_obj, f"/tmp/{pdf_id}/{pdf_id}_total.pdf")


def merge_and_upload(pdf_id, total_pages):
    pdf_obj_list = []
    for i in range(total_pages):
        page_n = i+1
        file_path = get_file_path(pdf_id, page_n)
        pdf_obj = fm.path_to_pdf_obj(file_path)
        pdf_obj_list.append(pdf_obj)

    merged_pdf_obj = fm.merge_pdf_pages(pdf_obj_list)
    merged_pdf_obj.stream.seek(0)
    compressed_url = None
    with StorageHandler() as handler:
        compressed_url = handler.upload(f"{pdf_id}_compressed.pdf", merged_pdf_obj.stream)
    shutil.rmtree(f"/tmp/{pdf_id}")

    return compressed_url


@app.task(name='register_result', bind=True, default_retry_delay=5)
def register_result(self, pdf_id, page_n, encoded_bytes):
    print(f"Recibi el resultado de la pagina {page_n} del pdf {pdf_id}")
    try:
        with S.begin():
            file_data = S.query(models.FileData).filter(models.FileData.id == pdf_id).one()
            note_task = file_data.note_task
            compress_subtask_id = note_task.compress_subtask.id

            task = S.query(models.CompressSubTask).with_for_update(of=models.CompressSubTask, nowait=True).get(compress_subtask_id)
            if task:
                process_pdf_obj(pdf_id, page_n, encoded_bytes)
                task.pages_done += 1
                task.status = models.BaseTaskStateEnum.in_progress if task.pages_done < file_data.page_count else models.BaseTaskStateEnum.done
                print(f"Proceso pagina {page_n}.. set actual: {task.pages_done_set}")
                if task.pages_done == 1:
                    task.pages_done_set = [page_n]
                else:
                    done_list = copy.copy(task.pages_done_set)
                    done_list.append(page_n)
                    task.pages_done_set = sorted(done_list)

                task.progress = int((task.pages_done / file_data.page_count) * 100)

                if task.pages_done == file_data.page_count:
                    compressed_url = merge_and_upload(pdf_id, file_data.page_count)
                    file_storage = file_data.file_storage
                    file_storage.compressed_url = compressed_url
                    S.add(file_storage)
                    app.send_task('register_subtask_completion', queue='backend',
                                  kwargs={'file_id': pdf_id, 'subtask': 'compress_subtask'})

                S.commit()
                print(f"Task {pdf_id}...page {page_n} updated")
            else:
                print(f"Task {pdf_id} not found")
    except StaleDataError:
        print("Another worker modified the row before this worker could lock it.")
    except OperationalError as exc:
        print(f"Pagina {page_n} OperationalError {exc}")
        if 'LockNotAvailable' in str(exc):
            print("Lock not available")
            S.rollback()
            print(f"Hago retry y raiseo {page_n}")
            raise self.retry(exc=exc)
        else:
            raise


def subtask_scheduler_handle(file_id, subtask):
    """
    Esta funcion se llama cuando finaliza una tarea y se encarga de verificar si se requiere disparar otra tarea
    """
    print(f"Checkeo el scheduler para {file_id} dado que se termino la subtask {subtask}")
    with S.begin():
        file_data = S.query(models.FileData).get(file_id)
        note_task = file_data.note_task
        fs = file_data.file_storage
        # Valido si requiero convertir a latex
        # Para convertirse a latex se deben dar las siguientes condiciones
        #    1 - El usuario seleccionó la opción de convertir a latex
        #    2 - La tarea precedente ha finalizado
        #      |_ 2.1 El usuario eligio comprimir y la compresion ha finalizado
        #      |_ 2.2 El usuario no eligio comprimir y la subida ha finalizado
        #
        # Como criterio para saber si una tarea finalizó o no me fijo si está disponible el campo de url relacionado
        if note_task.convert and subtask in ('compress_subtask', 'upload_subtask'):  # Para no validar de gusto
            print("Detecto que deberia pasar a Latex")
            if (note_task.compress and fs.compressed_url) or (not note_task.compress and fs.original_url):
                print(f"PERNO debo enviar a convertir a latex {file_id}")
                app.send_task('convert_to_latex', queue='backend', kwargs={'file_id': file_id})
            else:
                print("No se cumplieron las condiciones")

        # Valido si requiero buildear el latex
        if note_task.convert and subtask == 'latex_convert_subtask' and fs.latex_zip_url:
            if fs.latex_zip_url:
                print(f"PERNO debo enviar a buildear el latex {file_id}")
                app.send_task('build_latex', queue='latex_builder_queue', kwargs={'file_id': file_id,
                                                                                'latex_source': fs.latex_zip_url,
                                                                                'pdf_name': f"{file_id}_latex.pdf"})


@app.task(name='register_subtask_status')
def register_subtask_status(file_id, subtask, status):
    with (S.begin()):
        file_data = S.query(models.FileData).get(file_id)
        note_task = file_data.note_task
        subtask = getattr(note_task, subtask, None)
        status = getattr(models.BaseTaskStateEnum, status, None)
        if subtask and status:
            subtask.status = status
            flag_modified(note_task, 'last_updated')
            S.commit()


@app.task(name='register_subtask_completion')
def register_subtask_completion(file_id, subtask, subkwargs=None):
    print(f"Recibi como terminada tas {subtask} de file {file_id}")
    with (S.begin()):
        file_data = S.query(models.FileData).get(file_id)
        note_task = file_data.note_task
        subtask_obj = getattr(note_task, subtask, None)
        if subtask_obj:
            if subtask == 'latex_build_subtask':
                fs = file_data.file_storage
                fs.latex_pdf_url = subkwargs['pdf_url']
                print("Seteo el latex pdf url")
                S.add(fs)
            subtask_obj.status = models.BaseTaskStateEnum.done
            subtask_obj.progress = 100
            S.commit()
        else:
            print("No encuentro la subtask")

    with (S.begin()):
        file_data = S.query(models.FileData).get(file_id)
        note_task_id = file_data.note_task.id
        note_task = S.query(models.NoteTask).with_for_update(of=models.NoteTask).get(note_task_id)
        if note_task.status in (models.BaseTaskStateEnum.done, models.BaseTaskStateEnum.error):
            # Nothing to update
            pass
        else:
            status = None
            subtasks_str = ('upload_subtask', 'compress_subtask', 'latex_convert_subtask', 'latex_build_subtask')
            subtasks = [getattr(note_task, subtask_str) for subtask_str in subtasks_str]
            actual_subtasks = list(filter(lambda x: x is not None, subtasks))

            if any(subtask.status == models.BaseTaskStateEnum.error for subtask in actual_subtasks):
                print(f"Seteo la el file {file_id} en error")
                status = models.BaseTaskStateEnum.error
            elif all(subtask.status == models.BaseTaskStateEnum.done for subtask in actual_subtasks):
                status = models.BaseTaskStateEnum.done
                print(f"Seteo la el file {file_id} en done")
            elif any(subtask.status == models.BaseTaskStateEnum.in_progress for subtask in actual_subtasks) or any(subtask.status == models.BaseTaskStateEnum.done for subtask in actual_subtasks):
                status = models.BaseTaskStateEnum.in_progress
                print(f"Seteo la el file {file_id} en in progress")
            else:
                status = models.BaseTaskStateEnum.pending
                print(f"Seteo la el file {file_id} en pending")

            note_task.status = status
            flag_modified(note_task, 'last_updated')
            S.commit()
    subtask_scheduler_handle(file_id, subtask)


def update_non_finished_latex_tasks():
    print("Buscando tasks sin dato de procesado")
    mSubtask = models.LatexConvertSubTask
    mark_finished = []
    try:
        with S.begin():
            latex_tasks = S.query(mSubtask)\
                           .with_for_update(of=mSubtask)\
                           .filter(or_(and_(mSubtask.processing_status != 'completed', mSubtask.processing_status != 'error'),
                                       mSubtask.processing_status == None)).all()
            for latex_task in latex_tasks:
                job_id = latex_task.job_id
                note_task = latex_task.note_task
                if not job_id:
                    print(f"Encontre task sin job_id {latex_task.id}")
                    continue
                file_id = latex_task.file_data.id
                print(f"Encontre task sin terminar de procesar mathpix_id: {job_id}, file_id: {file_id}")
                result = mathpix.get_processing_status(job_id)
                if result:
                    print(f"El resultado es {result}")
                    progress, processing_status = result
                    latex_task.progress = int(progress/2)
                    latex_task.processing_status = processing_status
                    if processing_status == 'error':
                        mark_finished.append(latex_task.file_data.id)
                    S.add(latex_task)
                else:
                    # Treated as an error
                    mark_finished.append(latex_task.file_data.id)

                flag_modified(note_task, 'last_updated')
                S.add(note_task)
            S.commit()
    except StaleDataError:
        pass
    for file_id in mark_finished:
        app.send_task('register_subtask_completion', queue='backend',
                      kwargs={'file_id': file_id, 'subtask': 'latex_convert_subtask'})


def update_proceesed_but_not_converted_tasks():
    print("Buscando tasks sin dato de conversion")
    mSubtask = models.LatexConvertSubTask
    mark_finished = []
    try:
        with S.begin():
            latex_tasks = S.query(mSubtask)\
                           .with_for_update(of=mSubtask)\
                           .filter(and_(mSubtask.processing_status=="completed",
                                        or_(mSubtask.conversion_status == None,
                                            mSubtask.conversion_status == "processing")))\
                           .all()
            for latex_task in latex_tasks:
                note_task = latex_task.note_task
                job_id = latex_task.job_id
                print(f"Encontre task sin terminar de convertir {job_id}")
                result = mathpix.get_conversion_status(job_id)
                if result:
                    print(f"El resultado es {result}")
                    latex_task.conversion_status = result
                    if result == "completed":
                        latex_task.progress = 75
                    elif result == "error":
                        mark_finished.append(latex_task.file_data.id)
                    S.add(latex_task)
                else:
                    # Treated as an error
                    mark_finished.append(latex_task.file_data.id)

                flag_modified(note_task, 'last_updated')
                S.add(note_task)

        S.commit()
    except StaleDataError:
        pass

    for file_id in mark_finished:
        app.send_task('register_subtask_completion', queue='backend',
                      kwargs={'file_id': file_id, 'subtask': 'latex_convert_subtask'})


def update_not_uploaded_latex():
    print("Buscando tasks sin el latex subido")
    mSubtask = models.LatexConvertSubTask
    mark_finished = []
    try:
        with S.begin():
            latex_tasks = S.query(mSubtask).with_for_update(of=mSubtask)\
                           .filter(and_(mSubtask.conversion_status == "completed",
                                        mSubtask.processing_status == "completed",
                                        mSubtask.status == models.BaseTaskStateEnum.in_progress)).all()

            for latex_task in latex_tasks:
                note_task = latex_task.note_task
                file_data = latex_task.file_data
                file_storage = file_data.file_storage

                print(f"Encontre task sin subir {file_data.id}, mathpix job id: {latex_task.job_id}")
                result_bytes = mathpix.download_latex(latex_task.job_id)
                latex_task.progress = 100
                if not result_bytes:
                    print(f"Error en obtener la conversion a latex de {file_data.id}")
                    latex_task.status = models.BaseTaskStateEnum.error
                    continue
                else:
                    with StorageHandler() as handler:
                        latex_url = handler.upload(f"{file_data.id}.tex.zip", result_bytes)
                        file_storage.latex_zip_url = latex_url
                        S.add(file_storage)
                    latex_task.status = models.BaseTaskStateEnum.done
                S.add(latex_task)
                mark_finished.append(file_data.id)
            S.commit()

    except StaleDataError:
        pass

    for file_id in mark_finished:
        app.send_task('register_subtask_completion', queue='backend',
                      kwargs={'file_id': file_id, 'subtask': 'latex_convert_subtask'})


@app.task(name='update_current_jobs')
def update_current_jobs():
    update_non_finished_latex_tasks()
    update_proceesed_but_not_converted_tasks()
    update_not_uploaded_latex()


@app.task(name='convert_to_latex')
def convert_to_latex(file_id):
    with S.begin():
        file = S.query(models.FileData).get(file_id)
        file_storage = file.file_storage
        note_task = file.note_task
        file_url = file_storage.compressed_url or file_storage.original_url
        convert_latex_task = note_task.latex_convert_subtask

        flag_modified(note_task, 'last_updated')

        convert_latex_task.status = models.BaseTaskStateEnum.in_progress
        job_id = mathpix.send_pdf(file_url)
        if not job_id:
            convert_latex_task.status = models.BaseTaskStateEnum.error
        else:
            convert_latex_task.job_id = job_id

        S.add(convert_latex_task)
        S.add(note_task)
        S.commit()


app.conf.beat_schedule = {
    "check-every-minute": {
        "task": "update_current_jobs",
        "schedule": 30.0,
        "options": {"queue": "results"}
    }
}
