from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, models
from app.db import get_db
from app.schemas import UserResponse, UserCreate
from app.services import user_service
from fastapi import Path
from app.models import User
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserLogin
from app.services.auth import create_access_token

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.UserResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(db=db, user=user)


@router.get("/{user_id}", response_model=schemas.UserResponse)
def get_user(user_id: int = Path(..., title="ID użytkownika"), db: Session = Depends(get_db)):
    return db.query(models.User).filter(models.User.id == user_id).first()


@router.get("/all-users", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(models.User).all()


@router.delete("/{user_id}", response_model=dict, tags=["users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Deletes a user by ID.
    """
    try:
        user_service.delete_user(db, user_id)
        return {"message": f"User with ID {user_id} has been deleted."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already in use")

    hashed_password = User.hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not user.verify_password(user_data.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
