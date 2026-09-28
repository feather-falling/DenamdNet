"""
PostgreSQL Database connection and session management.
Uses SQLAlchemy ORM with connection pooling and thread-safe sessions.
"""

import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from ..config import settings

logger = logging.getLogger(__name__)

# Engine with pool_pre_ping to automatically recover from stale connections
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a SQLAlchemy database session and guarantees closure."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> bool:
    """Initializes database schema and ensures all tables exist.
    Safe to run repeatedly; will not alter or delete existing data.
    """
    try:
        from . import models  # noqa: F401
        Base.metadata.create_all(bind=engine)
        logger.info("PostgreSQL database tables initialized successfully.")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL database: {e}")
        return False
