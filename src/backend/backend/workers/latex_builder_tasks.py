from celery import Celery
from ..utils.storage import StorageHandler
from ..utils import file_manipulation as fm
from tempfile import TemporaryDirectory
import subprocess

app = Celery()
app.config_from_object('backend.common.latex_builder_tasks')

remote_app = Celery()
app.config_from_object('backend.common.backend_celeryconfig')

DEFAULT_SHELL_PATH = "/code/backend/scripts/build_latex.sh"


@app.task(name='build_latex')
def build_latex_task(file_id, latex_source, pdf_name):
    print(f"Recibo para construir el latex del file {latex_source}")
    app.send_task('register_subtask_status', queue='backend',
                  kwargs={'file_id': file_id, 'subtask': 'latex_build_subtask', 'status': 'in_progress'})
    with TemporaryDirectory() as tmp_dir:
        try:
            result = subprocess.run(["/bin/bash", DEFAULT_SHELL_PATH, latex_source, tmp_dir], check=True, capture_output=True)
            if result.returncode == 0:
                file_path = result.stdout.decode().rstrip('\n')
                print(f"El archivo se genero en {file_path}..subiendo como {pdf_name}..")
                pdf_obj = fm.path_to_pdf_obj(file_path)
                with StorageHandler() as storage:
                    pdf_url = storage.upload(pdf_name, pdf_obj.stream)
            else:
                print(f"Error al construir el latex: {result.stderr.decode()}")
        except subprocess.CalledProcessError:
            print("Error al construir el latex")
        except:
            print("Error inesperado")
            raise
    app.send_task('register_subtask_completion', queue='backend',
                  kwargs={'file_id': file_id, 'subtask': 'latex_build_subtask', 'subkwargs': {'pdf_url': pdf_url}})
