from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import Generator

from app.core.config import settings


# Create SQLAlchemy engine using DATABASE_URL from settings.
# If the URL points to a SQLite file use `check_same_thread=False`.
engine_kwargs = {"pool_pre_ping": True}
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite needs this argument when used with the default sync driver
    connect_args = {"check_same_thread": False}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, **engine_kwargs)

# Session factory for route dependencies or service layers
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator:
    """Yield a database session and ensure it's closed after use.

    This is used as a FastAPI dependency in endpoints:
    `db: Session = Depends(get_db)`
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
