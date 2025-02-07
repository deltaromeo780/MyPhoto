from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, RedirectResponse
from sqlalchemy.orm import Session
from io import BytesIO
from app.db import get_db
from app.models import Photo
from app.services import photo_service
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/photos", tags=["photos"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def get_all_photos(request: Request, db: Session = Depends(get_db)):
    photos = db.query(Photo).all()
    if not photos:
        raise HTTPException(status_code=404, detail="Brak zdjęć w bazie.")
    return templates.TemplateResponse("photos.html", {"request": request, "photos": photos})


@router.post("/")
async def upload_photo(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Plik nie jest zdjęciem.")
    await photo_service.upload_photo(file, db)
    return RedirectResponse(url="/photos", status_code=303)


@router.get("/{photo_id}")
def get_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = photo_service.get_photo(photo_id, db)
    if not photo:
        raise HTTPException(status_code=404, detail="Zdjęcie nie znalezione.")
    return StreamingResponse(
        BytesIO(photo.data),
        media_type=photo.content_type,
        headers={"Content-Disposition": f"inline; filename={photo.filename}"}
    )


@router.delete("/{photo_id}")
def delete_photo(photo_id: int, db: Session = Depends(get_db)):
    photo = photo_service.delete_photo(photo_id, db)
    if not photo:
        raise HTTPException(status_code=404, detail="Zdjęcie nie znalezione.")
    return {"message": f"Zdjęcie o ID {photo_id} zostało usunięte."}