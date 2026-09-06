"""Health check endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.api.dependencies import get_db

router = APIRouter()


@router.get("/health")
def health_check():
    """Basic health check."""
    return {"status": "healthy", "service": "staj-platform"}


@router.get("/health/db")
def db_health_check(db: Session = Depends(get_db)):
    """Database connectivity check."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
