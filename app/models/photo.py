from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship

from app.db import Base


class Photo(Base):
    """
    ORM model representing a photo stored in the database.
    """
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    content_type = Column(String)
    data = Column(LargeBinary)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))  # Dodajemy ondelete="CASCADE"

    user = relationship("User", back_populates="photos")
