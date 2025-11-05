from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """
    Database session dependency for FastAPI routes.

    Yields a database session and ensures it is properly closed after use.
    This function should be used with FastAPI's Depends() for dependency injection.

    Yields:
        Session: SQLAlchemy database session

    Example:
        @router.get("/")
        async def get_items(db: Session = Depends(get_db)):
            return db.query(Model).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
