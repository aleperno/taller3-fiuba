from unittest.mock import MagicMock
import pytest
from unittest import mock

from mock_alchemy.mocking import UnifiedAlchemyMagicMock
from src.tasks.task_repository import TaskRepository
from src.tasks.task import Task

@pytest.fixture
def db_mock():
    def update_task_id(task):
        task.id = "created_id"
        return task
    
    db_mock = UnifiedAlchemyMagicMock(data=[
        (
            [mock.call.query(Task), mock.call.filter(Task.id == "get_task_id")],
            [Task(id="get_task_id")]
        ),
        (
            [mock.call.query(Task)],
            [Task(id=1), Task(id=2), Task(id=3)]
        )
    ])

    db_mock.refresh = MagicMock(side_effect=update_task_id)
    return db_mock

@pytest.fixture
def task_repository(db_mock):
    return TaskRepository(db_mock)

def test_create(task_repository):
    created_task = task_repository.create(Task())
    task_repository.db.add.assert_called_once()
    task_repository.db.commit.assert_called_once()
    assert created_task.id == "created_id"

def test_get(task_repository):
    task = task_repository.get("get_task_id")
    assert task.id == "get_task_id"

def test_get_all(task_repository):
    tasks = task_repository.get_all()
    assert tasks[0].id == 1
    assert tasks[1].id == 2
    assert tasks[2].id == 3
