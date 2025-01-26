# Funkcja do usuwania zdjęcia
from sqlalchemy.orm import Session

from app import models


def delete_photo(db: Session, photo_id: int):
    db_photo = db.query(models.Photo).filter(models.Photo.id == photo_id).first()
    if db_photo:
        db.delete(db_photo)
        db.commit()
    return db_photo
