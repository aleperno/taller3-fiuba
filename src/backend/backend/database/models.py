import uuid
import enum
from sqlalchemy import Boolean, Column, Enum, ForeignKey, Integer, String, JSON, URL, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy_utils import UUIDType
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr

from . import Base


class FilePrivacyEnum(enum.Enum):
    public = "public"
    private = "private"
    restricted = "restricted"


class BaseTaskStateEnum(enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    done = "done"
    error = "error"


class NoteTaskCurrentProcessEnum(enum.Enum):
    pending = "pending"
    uploading = "uploading"
    compressing = "compressing"
    converting = "converting"
    building = "building"
    done = "done"


class TaskStateEnum(enum.Enum):
    pending = "pending"
    compressing = "compressing"
    preprocessing = 'preprocessing'
    done = "done"
    error = "error"


class LatexProcessingStatusEnum(enum.Enum):
    """
    Reference: https://docs.mathpix.com/#processing-status
    """
    received = "received"
    loaded = "loaded"
    split = "split"
    completed = "completed"
    error = "error"


class LatexConvertionStatusEnum(enum.Enum):
    """
    Reference: https://docs.mathpix.com/#get-conversion-status
    """
    processing = "processing"
    completed = "completed"
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


class User(BaseClass, Base):
    __tablename__ = "user"
    _shown_attrs = ["id", "email"]

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Relationships
    file_data = relationship("FileData", back_populates="user", cascade="all, delete-orphan", uselist=True)


class FileData(BaseClass, Base):
    __tablename__ = "file_data"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    file_name = Column(String, nullable=False)
    page_count = Column(Integer, nullable=False)
    privacy = Column(Enum(FilePrivacyEnum), nullable=False)
    user_id = Column(UUIDType(binary=False), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Relationships
    user = relationship("User", back_populates="file_data", uselist=False)
    shared_data = relationship("SharedData", back_populates="file", cascade="all, delete-orphan", uselist=True)
    file_storage = relationship("FileStorage", back_populates="file", cascade="all, delete-orphan", uselist=False)
    note_task = relationship("NoteTask", back_populates="file", cascade="all, delete-orphan", uselist=False)


class SharedData(BaseClass, Base):
    __tablename__ = "shared_data"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUIDType(binary=False), ForeignKey("file_data.id", ondelete="CASCADE"), nullable=False)
    email = Column(String, nullable=False)
    # Relationships
    file = relationship("FileData", back_populates="shared_data")


class FileStorage(BaseClass, Base):
    __tablename__ = "file_storage"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUIDType(binary=False), ForeignKey("file_data.id", ondelete="CASCADE"), nullable=False)
    original_url = Column(String, nullable=True)
    compressed_url = Column(String, nullable=True)
    latex_zip_url = Column(String, nullable=True)
    latex_pdf_url = Column(String, nullable=True)
    # Relationships
    file = relationship("FileData", back_populates="file_storage")


class NoteTask(BaseClass, Base):
    __tablename__ = "note_task"

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUIDType(binary=False), ForeignKey("file_data.id", ondelete="CASCADE"), nullable=False)
    compress = Column(Boolean, default=False, nullable=False)
    convert = Column(Boolean, default=False, nullable=False)
    status = Column(Enum(BaseTaskStateEnum), default=BaseTaskStateEnum.pending)
    current_process = Column(Enum(NoteTaskCurrentProcessEnum), default=NoteTaskCurrentProcessEnum.pending)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    file = relationship("FileData", back_populates="note_task")
    upload_subtask = relationship("UploadSubTask", back_populates="note_task", cascade="all, delete-orphan", uselist=False)
    compress_subtask = relationship("CompressSubTask", back_populates="note_task", cascade="all, delete-orphan", uselist=False)
    latex_convert_subtask = relationship("LatexConvertSubTask", back_populates="note_task", cascade="all, delete-orphan", uselist=False)
    latex_build_subtask = relationship("LatexBuildSubTask", back_populates="note_task", cascade="all, delete-orphan", uselist=False)

    @property
    def user(self):
        return self.file.user


class SubTask(BaseClass, Base):
    __abstract__ = True

    id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
    @declared_attr
    def note_task_id(cls):
        return Column(UUIDType(binary=False), ForeignKey("note_task.id", ondelete="CASCADE"), nullable=False)
    progress = Column(Integer, default=0, nullable=False)
    status = Column(Enum(BaseTaskStateEnum), default=BaseTaskStateEnum.pending)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())


    @property
    def file_data(self):
        return self.note_task.file


class UploadSubTask(SubTask):
    __tablename__ = 'upload_subtask'

    note_task = relationship("NoteTask", back_populates="upload_subtask")


class CompressSubTask(SubTask):
    __tablename__ = 'compress_subtask'

    colours = Column(Integer, default=5, nullable=False)
    white_background = Column(Boolean, default=False, nullable=False)
    pages_done = Column(Integer, default=0)
    pages_done_set = Column(JSON, nullable=True)
    note_task = relationship("NoteTask", back_populates="compress_subtask")


class LatexConvertSubTask(SubTask):
    __tablename__ = 'latex_convert_subtask'

    job_id = Column(String, nullable=True)  # Mathpix job_id
    processing_status = Column(Enum(LatexProcessingStatusEnum), nullable=True)
    conversion_status = Column(Enum(LatexConvertionStatusEnum), nullable=True)
    note_task = relationship("NoteTask", back_populates="latex_convert_subtask")


class LatexBuildSubTask(SubTask):
    __tablename__ = 'latex_build_subtask'

    note_task = relationship("NoteTask", back_populates="latex_build_subtask")
