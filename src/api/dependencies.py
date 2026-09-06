"""FastAPI dependency injection."""

from typing import Generator
from sqlalchemy.orm import Session

from src.storage.engine import get_engine, get_session_factory

_engine = None
_session_factory = None


def get_db() -> Generator[Session, None, None]:
    """Yield a database session for request scope."""
    global _engine, _session_factory
    if _engine is None:
        _engine = get_engine()
    if _session_factory is None:
        _session_factory = get_session_factory(_engine)
    
    session = _session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
