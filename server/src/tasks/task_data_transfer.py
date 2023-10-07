from pydantic import BaseModel
from typing import List, Optional, Union
from uuid import UUID

from src.tasks.task import TaskState

class CreateTaskRequest(BaseModel):
    global_palette_opt: bool
    white_background: bool
    colours: int
    total_pages: int
    selected_pages: List[int]

class TaskRequest(BaseModel):
    id: UUID

class TaskResponse(BaseModel):
    id: UUID
    global_palette_opt: Optional[bool]
    white_background: bool
    colours: int
    total_pages: int
    pages_done: int
    selected_pages: list
    status: TaskState
