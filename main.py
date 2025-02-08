from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.db import Base, engine
from app.routes import photos, users

# Inicjalizacja bazy danych
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def main_page(request: Request):
    return templates.TemplateResponse("main.html", {"request": request})


# Rejestracja routerów
app.include_router(photos.router)
app.include_router(users.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
