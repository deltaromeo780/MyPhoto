from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from io import BytesIO
from app.db import Base, engine, get_db
from app.models import Photo
from app import crud, schemas


# Inicjalizacja bazy danych
Base.metadata.create_all(bind=engine)


# Inicjalizacja aplikacji FastAPI
app = FastAPI()


# Inicjalizacja statycznych plików i szablonów
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def main_page(request: Request):
    """Strona główna aplikacji."""
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/photos/")
def get_all_photos(request: Request, db: Session = Depends(get_db)):
    """Pobieranie wszystkich zdjęć i renderowanie szablonu HTML."""
    photos = db.query(Photo).all()
    if not photos:
        raise HTTPException(status_code=404, detail="Brak zdjęć w bazie.")
    return templates.TemplateResponse("photos.html", {"request": request, "photos": photos})


@app.post("/photos/")
async def upload_photo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Przesyłanie zdjęcia i zapis do bazy danych."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Plik nie jest zdjęciem.")
    photo = Photo(
        filename=file.filename,
        content_type=file.content_type,
        data=await file.read()
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return RedirectResponse(url="/photos", status_code=303)


@app.get("/photos/{photo_id}")
def get_photo(photo_id: int, db: Session = Depends(get_db)):
    """Pobieranie zdjęcia z bazy danych."""
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Zdjęcie nie znalezione.")
    return StreamingResponse(
        BytesIO(photo.data),
        media_type=photo.content_type,
        headers={"Content-Disposition": f"inline; filename={photo.filename}"}
    )


@app.delete("/photos/{photo_id}")
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    """Usuwanie zdjęcia z bazy danych."""
    photo = db.query(Photo).filter(Photo.id == photo_id).first()
    if not photo:
        raise HTTPException(status_code=404, detail="Zdjęcie nie znalezione.")
    db.delete(photo)
    db.commit()
    return {"message": f"Zdjęcie o ID {photo_id} zostało usunięte."}


@app.post("/users/", response_model=schemas.UserResponse, tags=["users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Tworzenie nowego użytkownika."""
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/{user_id}", response_model=schemas.UserResponse, tags=["users"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    """Pobieranie danych użytkownika po ID."""
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
