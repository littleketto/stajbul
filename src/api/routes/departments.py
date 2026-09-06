"""Department reference data endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from src.api.dependencies import get_db
from src.storage.repositories import DepartmentRepository
from src.models.schemas import DepartmentSchema

router = APIRouter()


@router.get("/departments", response_model=list[DepartmentSchema])
def list_departments(
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search departments"),
    db: Session = Depends(get_db),
):
    """List all departments, optionally filtered by category or search query."""
    repo = DepartmentRepository(db)
    
    if search:
        return [DepartmentSchema.model_validate(d) for d in repo.search(search)]
    elif category:
        return [DepartmentSchema.model_validate(d) for d in repo.get_by_category(category)]
    else:
        return [DepartmentSchema.model_validate(d) for d in repo.get_all()]
