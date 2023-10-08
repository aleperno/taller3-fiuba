import pytest
from unittest.mock import MagicMock, Mock

from src.tasks.task import Task
from src.tasks.task_getter import TaskGetter

@pytest.fixture
def task_repository_mock():
    def get_task(task_id):
        return Task(id=task_id)

    task_repository_mock = Mock()
    task_repository_mock.get = MagicMock(side_effect=get_task)
    task_repository_mock.get_all.return_value = [Task(id="task_1"), Task(id="task_2")]
    return task_repository_mock

@pytest.fixture
def task_getter(task_repository_mock):
    return TaskGetter(task_repository_mock)

def test_get_by_id(task_getter):
    task = task_getter.get_task("get_task")
    assert task.id == "get_task"
    assert task_getter.task_repository.get.call_count == 1

def test_get_all(task_getter):
    tasks = task_getter.get_tasks()
    assert tasks[0].id == "task_1"
    assert tasks[1].id == "task_2"
    assert task_getter.task_repository.get_all.call_count == 1