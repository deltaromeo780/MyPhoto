from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.db import get_db
from app.services import user_service
from fastapi import Path


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(db=db, user=user)


@router.get("/users/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int = Path(..., title="ID użytkownika"), db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.id == user_id).first()


@router.get("/all-users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@router.delete("/users/{user_id}", response_model=dict, tags=["users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Deletes a user by ID.
    """
    try:
        user_service.delete_user(db, user_id)
        return {"message": f"User with ID {user_id} has been deleted."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
