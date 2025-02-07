from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from io import BytesIO
from app.db import Base, engine, get_db
from app.models import Photo
from app import schemas
from app.services import user_service, photo_service
import uvicorn

# Initialization database
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


@app.get("/photos/")
def get_all_photos(request: Request, db: Session = Depends(get_db)):
    photos = db.query(Photo).all()
    if not photos:
        raise HTTPException(status_code=404, detail="Brak zdjęć w bazie.")
    return templates.TemplateResponse("photos.html", {"request": request, "photos": photos})


@app.post("/photos/")
async def upload_photo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Plik nie jest zdjęciem.")
    photo = await photo_service.upload_photo(file, db)
    return RedirectResponse(url="/photos", status_code=303)


@app.get("/photos/{photo_id}")
def get_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = photo_service.get_photo(photo_id, db)
    if not photo:
        raise HTTPException(status_code=404, detail="Zdjęcie nie znalezione.")
    return StreamingResponse(
        BytesIO(photo.data),
        media_type=photo.content_type,
        headers={"Content-Disposition": f"inline; filename={photo.filename}"}
    )


@app.delete("/photos/{photo_id}")
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = photo_service.delete_photo(photo_id, db)
    if not photo:
        raise HTTPException(status_code=404, detail="Zdjęcie nie znalezione.")
    return {"message": f"Zdjęcie o ID {photo_id} zostało usunięte."}


@app.post("/users/", response_model=schemas.UserResponse, tags=["users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = user_service.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(db=db, user=user)


@app.get("/users/{user_id}", response_model=schemas.UserResponse, tags=["users"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
