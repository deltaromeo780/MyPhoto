from sqlalchemy import Column, Integer, String, LargeBinary
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from app.db import Base


# Model ORM dla bazy danych
class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    content_type = Column(String)
    data = Column(LargeBinary)  # Przechowywanie bajtów pliku


# Model Pydantic do walidacji
class PhotoCreate(BaseModel):
    filename: str
    content_type: str
    data: bytes
