import uuid
import enum
from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType


from . import Base


class TaskStateEnum(enum.Enum):
    pending = "pending"
    compressing = "compressing"
    preprocessing = 'preprocessing'
    done = "done"
    error = "error"


class BaseClass(object):
    _shown_attrs = ["id", "name"]

    @property
    def verbose_name(self):
        return self.__class__.__name__

    def __repr__(self):
        attrs = []
        for attr_name in self._shown_attrs:
            attr = getattr(self, attr_name, None)
            if attr is not None and not callable(attr):
                attrs.append(f"{attr_name}={attr}")
        return f"{self.verbose_name} ({', '.join(attrs)})"


class CompressTask(BaseClass, Base):
    __tablename__ = "compress_task"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    global_palette_opt = Column(Boolean, default=False, nullable=False)
    white_background = Column(Boolean, default=True, nullable=False)
    colours = Column(Integer, default=80, nullable=False)
    total_pages = Column(Integer, nullable=False)
    pages_done = Column(Integer, default=0)
    global_palette = Column(JSON, nullable=True)
    status = Column(Enum(TaskStateEnum), default=TaskStateEnum.pending)
