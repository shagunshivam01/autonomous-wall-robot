"""FastAPI dependency injection."""
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.logging_config import get_correlation_id, get_logger
from app.persistence.database import get_db, SessionLocal

logger = get_logger(__name__)


def get_db_session() -> Session:
    """Yield database session for dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
