from pydantic import BaseModel, Json
from typing import Optional, Any, Union, List
from uuid import UUID
from .models import TaskStateEnum


class TaskRequestBase(BaseModel):
    global_palette_opt: bool
    white_background: bool
    colours: int
    total_pages: int
    selected_pages: List[int]


class TaskRequest(BaseModel):
    id: str


class TaskResponse(TaskRequest, TaskRequestBase):
    id: UUID
    pages_done: int
    global_palette: Optional[Union[dict, None]]
    status: TaskStateEnum

    class Config:
        orm_mode = True
        use_enum_values = True


class ImageUpload(BaseModel):
    file_content: str
