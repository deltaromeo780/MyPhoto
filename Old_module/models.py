from sqlalchemy import Column, Integer, String, LargeBinary
from pydantic import BaseModel
from app.db import Base


# Model ORM dla bazy danych
class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    content_type = Column(String)
    data = Column(LargeBinary)


# Model Pydantic do walidacji
class PhotoCreate(BaseModel):
    filename: str
    content_type: str
    data: bytes


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
