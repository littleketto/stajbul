"""Internship listing API endpoints."""

import math
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date

from src.api.dependencies import get_db
from src.storage.repositories import ListingRepository
from src.models.schemas import (
    InternshipListingSchema,
    ListingFilterParams,
    ListingListResponse,
    ExtractedInternshipData,
)
from src.models.enums import (
    StudentLevel,
    DepartmentCategory,
    WorkModality,
    InternshipType,
)

router = APIRouter()


@router.get("/listings", response_model=ListingListResponse)
def list_listings(
    keyword: Optional[str] = Query(None, description="Search keyword"),
    city: Optional[str] = Query(None, description="City filter"),
    eligible_level: Optional[StudentLevel] = Query(None, description="Student level filter"),
    department_category: Optional[DepartmentCategory] = Query(None, description="Department category"),
    department_name: Optional[str] = Query(None, description="Department name search"),
    work_modality: Optional[WorkModality] = Query(None, description="Work modality"),
    internship_type: Optional[InternshipType] = Query(None, description="Internship type"),
    is_paid: Optional[bool] = Query(None, description="Paid internship filter"),
    requires_mandatory_letter: Optional[bool] = Query(None, description="Mandatory letter filter"),
    min_days_per_week_max: Optional[int] = Query(None, description="Max days per week"),
    posted_after: Optional[date] = Query(None, description="Posted after date"),
    deadline_before: Optional[date] = Query(None, description="Deadline before date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: str = Query("posted_date_desc", description="Sort order"),
    db: Session = Depends(get_db),
):
    """List and filter enriched internship listings."""
    params = ListingFilterParams(
        keyword=keyword,
        city=city,
        eligible_level=eligible_level,
        department_category=department_category,
        department_name=department_name,
        work_modality=work_modality,
        internship_type=internship_type,
        is_paid=is_paid,
        requires_mandatory_letter=requires_mandatory_letter,
        min_days_per_week_max=min_days_per_week_max,
        posted_after=posted_after,
        deadline_before=deadline_before,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
    )
    
    repo = ListingRepository(db)
    listings, total = repo.filter_listings(params)
    
    return ListingListResponse(
        items=[InternshipListingSchema.model_validate(l) for l in listings],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 0,
    )


@router.get("/listings/{listing_id}", response_model=InternshipListingSchema)
def get_listing(listing_id: int, db: Session = Depends(get_db)):
    """Get a specific listing by ID."""
    repo = ListingRepository(db)
    listing = repo.get_by_id(listing_id)
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    return InternshipListingSchema.model_validate(listing)


@router.get("/listings/stats/summary")
def get_stats(db: Session = Depends(get_db)):
    """Get platform statistics."""
    repo = ListingRepository(db)
    return repo.get_stats()
