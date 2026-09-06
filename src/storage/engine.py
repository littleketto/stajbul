"""Database engine and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

from src.config.settings import get_settings
from src.models.database import Base


def get_engine(database_url: str | None = None):
    """Create and return a SQLAlchemy engine."""
    settings = get_settings()
    url = database_url or settings.database_url
    engine = create_engine(
        url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=False,
    )
    return engine


def get_session_factory(engine=None):
    """Create and return a session factory."""
    if engine is None:
        engine = get_engine()
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


@contextmanager
def get_db_session(engine=None) -> Session:
    """Context manager for database sessions with auto commit/rollback."""
    SessionFactory = get_session_factory(engine)
    session = SessionFactory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(engine=None):
    """Initialize database by creating all tables."""
    if engine is None:
        engine = get_engine()
    Base.metadata.create_all(bind=engine)
    return engine


def drop_db(engine=None):
    """Drop all tables. USE WITH CAUTION."""
    if engine is None:
        engine = get_engine()
    Base.metadata.drop_all(bind=engine)
