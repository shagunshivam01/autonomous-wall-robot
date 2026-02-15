"""SQLAlchemy database engine, session, and base configuration."""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings

settings = get_settings()

# SQLite with WAL mode for better concurrency
connect_args = {"check_same_thread": False} if "sqlite" in settings.database_url else {}
engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    poolclass=StaticPool if "sqlite" in settings.database_url else None,
    echo=settings.debug,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    """Create all tables and enable WAL for SQLite."""
    from app.persistence.trajectory_model import TrajectoryModel  # noqa: F401
    Base.metadata.create_all(bind=engine)
    if "sqlite" in settings.database_url:
        with engine.connect() as conn:
            conn.execute(text("PRAGMA journal_mode=WAL"))
            conn.execute(text("PRAGMA synchronous=NORMAL"))
            conn.execute(text("PRAGMA cache_size=-64000"))
            conn.commit()


def get_db():
    """Dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
