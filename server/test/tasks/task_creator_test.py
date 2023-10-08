from unittest.mock import MagicMock, Mock
import pytest

from src.tasks.task_creator import TaskCreator
from src.tasks.task_data_transfer import CreateTaskRequest
from src.tasks.task import Task

@pytest.fixture
def task_repository_mock():
    def create_task(create_task_request: CreateTaskRequest):
        return Task(id="created_task",
                    global_palette_opt=create_task_request.global_palette_opt,
                    white_background=create_task_request.white_background,
                    colours=create_task_request.colours,
                    total_pages=create_task_request.total_pages,
                    selected_pages=create_task_request.selected_pages
        )

    task_repository_mock = Mock()
    task_repository_mock.create = MagicMock(side_effect=create_task)
    return task_repository_mock

@pytest.fixture
def celery_mock():
    return Mock()

@pytest.fixture
def task_creator(task_repository_mock, celery_mock):
    return TaskCreator(task_repository_mock, celery_mock)

def test_create_task(task_creator):
    task_request = CreateTaskRequest(
        global_palette_opt=True,
        white_background=True,
        colours=5,
        total_pages=2,
        selected_pages=[0,1]
    )
    task = task_creator.create_task(task_request)
    task_creator.task_repository.create.assert_called_once()
    assert task_creator.celery_app.send_task.call_count == 2
    assert task.id == "created_task"
    assert task.white_background == True
    assert task.colours == 5
    assert task.total_pages == 2
    assert task.selected_pages == [0,1]
