from sqlalchemy.orm import Session
from app import models


def delete_photo(db: Session, photo_id: int):
    """
    Deletes a photo from the database.
    """
    db_photo = db.query(models.Photo).filter(models.Photo.id == photo_id).first()
    if db_photo:
        db.delete(db_photo)
        db.commit()
    return db_photo


from sqlalchemy.orm import Session
from fastapi import UploadFile
from app import models


async def upload_photo(file: UploadFile, db: Session):
    """
    Saves a photo to the database.
    """
    photo = models.Photo(
        filename=file.filename,
        content_type=file.content_type,
        data=await file.read()
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


def get_photo(photo_id: int, db: Session):
    """
    Retrieves a photo by ID.
    """
    return db.query(models.Photo).filter(models.Photo.id == photo_id).first()


def delete_photo(photo_id: int, db: Session):
    """
    Deletes a photo from the database.
    """
    photo = db.query(models.Photo).filter(models.Photo.id == photo_id).first()
    if photo:
        db.delete(photo)
        db.commit()
    return photo

