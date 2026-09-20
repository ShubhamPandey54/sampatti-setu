from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# check_same_thread=False is needed only for SQLite + FastAPI's threaded dev server.
engine = create_engine(
    settings.sqlite_url,
    connect_args={"check_same_thread": False} if settings.sqlite_url.startswith("sqlite") else {},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
