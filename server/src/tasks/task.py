import uuid
import enum
from sqlalchemy import Boolean, Column, Enum, Integer, JSON
from sqlalchemy_utils import UUIDType

from src.database import Base

class TaskState(enum.Enum):
    pending = "pending"
    compressing = "compressing"
    preprocessing = 'preprocessing'
    done = "done"
    error = "error"

class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    global_palette_opt = Column(Boolean, default=False, nullable=False)
    white_background = Column(Boolean, default=True, nullable=False)
    colours = Column(Integer, default=80, nullable=False)
    total_pages = Column(Integer, nullable=False)
    pages_done = Column(Integer, default=0)
    global_palette = Column(JSON, nullable=True)
    selected_pages = Column(JSON, nullable=False)
    status = Column(Enum(TaskState), default=TaskState.pending)
