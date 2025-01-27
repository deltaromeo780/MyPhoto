from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = SQLALCHEMY_DATABASE_URL = "postgresql://user:Eileen_90@localhost/myphoto_db"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Funkcja pomocnicza do zarządzania sesją bazy danych."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
