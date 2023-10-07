import pytest
from src.tasks.task import Task

@pytest.fixture
def task():
    return Task(
        global_palette_opt=True,
        white_background=True,
        colours=2,
        total_pages=5,
        pages_done=0,
        global_palette={},
        selected_pages=[0,1,2,3,4]
    )

def test_constructor(task):
    assert task.global_palette_opt == True