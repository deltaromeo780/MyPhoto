from sqlalchemy.orm import Session
from app import models, schemas
from passlib.context import CryptContext
from fastapi import HTTPException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db: Session, user_id: int):
    """
    Retrieves a user by ID.
    """
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    """
    Retrieves a user by email.
    """
    return db.query(models.User).filter(models.User.email == email).first()


def create_user(db: Session, user: schemas.UserCreate):
    """
    Creates a new user with hashed password.
    """
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Jeśli użytkownik ma zdjęcia, usuwamy je przed usunięciem użytkownika
    db.query(models.Photo).filter(models.Photo.user_id == user_id).delete()

    db.delete(user)
    db.commit()


def get_users(db: Session):
    """
    Retrieves all users from the database.
    """
    return db.query(models.User).all()
