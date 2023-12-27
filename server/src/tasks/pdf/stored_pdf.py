import uuid
from sqlalchemy import String, Column
from sqlalchemy_utils import UUIDType

from src.database import Base

class StoredPdf(Base):
  __tablename__ = "stored_pdfs"
  id = Column(UUIDType(binary=False), primary_key=True, default=uuid.uuid4)
  id = Column(String, nullable=False)
