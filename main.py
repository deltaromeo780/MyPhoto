from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from io import BytesIO

from app.db import Base, engine, get_db
from app.models import Photo

# Inicjalizacja bazy danych
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/photos/")
async def upload_photo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Przesyłanie zdjęcia i zapis do bazy danych."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Plik nie jest zdjęciem.")

    photo = Photo(
        filename=file.filename,
        content_type=file.content_type,
        data=await file.read()  # Odczyt danych pliku
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)

    return {"id": photo.id, "filename": photo.filename}

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
