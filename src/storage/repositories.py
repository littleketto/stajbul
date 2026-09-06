"""Repository layer for database CRUD operations."""

from datetime import datetime, date
from typing import Optional

from sqlalchemy import select, func, and_, or_, cast, String
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import JSONB

from src.models.database import InternshipListingDB, DepartmentDB
from src.models.enums import ListingStatus, SourcePlatform
from src.models.schemas import (
    ScrapedJobCard,
    ExtractedInternshipData,
    ListingFilterParams,
)


class ListingRepository:
    """Repository for internship listing operations."""

    def __init__(self, session: Session):
        self.session = session

    # ── Create / Upsert ──

    def upsert_from_job_card(
        self,
        card: ScrapedJobCard,
        source_platform: SourcePlatform = SourcePlatform.LINKEDIN,
        batch_id: str | None = None,
    ) -> tuple[InternshipListingDB, bool]:
        """
        Insert a new listing from a scraped job card, or update last_seen_at if it already exists.
        Returns (listing, is_new) tuple.
        """
        existing = self.get_by_source_id(source_platform.value, card.job_id)
        if existing:
            existing.last_seen_at = datetime.utcnow()
            return existing, False

        listing = InternshipListingDB(
            source_platform=source_platform.value,
            source_job_id=card.job_id,
            source_url=card.url,
            raw_title=card.title,
            raw_company=card.company,
            raw_location=card.location,
            posted_date=card.posted_date,
            status=ListingStatus.RAW.value,
            first_seen_at=datetime.utcnow(),
            last_seen_at=datetime.utcnow(),
            scrape_batch_id=batch_id,
        )
        self.session.add(listing)
        self.session.flush()  # Get the ID without committing
        return listing, True

    def update_with_detail(
        self,
        source_job_id: str,
        description_text: str,
        description_html: str | None = None,
        seniority_level: str | None = None,
        employment_type: str | None = None,
        source_platform: str = "LINKEDIN",
    ) -> InternshipListingDB | None:
        """Update a listing with the full description fetched from detail endpoint."""
        listing = self.get_by_source_id(source_platform, source_job_id)
        if not listing:
            return None
        listing.raw_description_text = description_text
        listing.raw_description_html = description_html
        listing.status = ListingStatus.SCRAPED.value
        return listing

    def update_with_enrichment(
        self,
        listing_id: int,
        enriched: ExtractedInternshipData,
        model_used: str,
        token_count: int | None = None,
    ) -> InternshipListingDB | None:
        """Update a listing with LLM-extracted enriched data."""
        listing = self.get_by_id(listing_id)
        if not listing:
            return None

        # Store full enriched data as JSON
        listing.enriched_data = enriched.model_dump(mode="json")
        listing.status = ListingStatus.ENRICHED.value
        listing.enriched_at = datetime.utcnow()
        listing.llm_model_used = model_used
        listing.llm_token_count = token_count

        # Denormalize frequently-filtered fields
        listing.city = enriched.city
        listing.work_modality = enriched.work_modality
        listing.work_schedule = enriched.work_schedule
        listing.internship_type = enriched.internship_type
        listing.is_paid = enriched.is_paid
        listing.requires_mandatory_letter = enriched.requires_mandatory_internship_letter
        listing.application_deadline = enriched.application_deadline
        listing.min_days_per_week = enriched.min_days_per_week
        listing.summary_tr = enriched.summary_tr
        listing.extraction_confidence = enriched.extraction_confidence

        # Denormalize JSON arrays
        listing.eligible_levels_json = [l.value if hasattr(l, 'value') else l for l in enriched.eligible_levels]
        listing.department_categories_json = [c.value if hasattr(c, 'value') else c for c in enriched.department_categories]
        listing.eligible_departments_json = enriched.eligible_departments
        listing.required_skills_json = enriched.required_skills

        return listing

    def mark_failed(self, listing_id: int, reason: str | None = None) -> None:
        """Mark a listing as failed during enrichment."""
        listing = self.get_by_id(listing_id)
        if listing:
            listing.status = ListingStatus.FAILED.value

    # ── Read ──

    def get_by_id(self, listing_id: int) -> InternshipListingDB | None:
        return self.session.get(InternshipListingDB, listing_id)

    def get_by_source_id(
        self, source_platform: str, source_job_id: str
    ) -> InternshipListingDB | None:
        stmt = select(InternshipListingDB).where(
            and_(
                InternshipListingDB.source_platform == source_platform,
                InternshipListingDB.source_job_id == source_job_id,
            )
        )
        return self.session.execute(stmt).scalar_one_or_none()

    def get_raw_listings(self, limit: int = 100) -> list[InternshipListingDB]:
        """Get listings with status=RAW (need detail fetching)."""
        stmt = (
            select(InternshipListingDB)
            .where(InternshipListingDB.status == ListingStatus.RAW.value)
            .order_by(InternshipListingDB.first_seen_at.asc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    def get_scraped_listings(self, limit: int = 100) -> list[InternshipListingDB]:
        """Get listings with status=SCRAPED (need LLM enrichment)."""
        stmt = (
            select(InternshipListingDB)
            .where(InternshipListingDB.status == ListingStatus.SCRAPED.value)
            .order_by(InternshipListingDB.first_seen_at.asc())
            .limit(limit)
        )
        return list(self.session.execute(stmt).scalars().all())

    def filter_listings(
        self, params: ListingFilterParams
    ) -> tuple[list[InternshipListingDB], int]:
        """
        Filter enriched listings based on query parameters.
        Returns (listings, total_count) for pagination.
        """
        stmt = select(InternshipListingDB).where(
            InternshipListingDB.status == ListingStatus.ENRICHED.value
        )
        count_stmt = select(func.count(InternshipListingDB.id)).where(
            InternshipListingDB.status == ListingStatus.ENRICHED.value
        )

        # Apply filters
        if params.keyword:
            keyword_filter = or_(
                InternshipListingDB.raw_title.ilike(f"%{params.keyword}%"),
                InternshipListingDB.raw_company.ilike(f"%{params.keyword}%"),
                InternshipListingDB.summary_tr.ilike(f"%{params.keyword}%"),
            )
            stmt = stmt.where(keyword_filter)
            count_stmt = count_stmt.where(keyword_filter)

        if params.city:
            stmt = stmt.where(InternshipListingDB.city == params.city)
            count_stmt = count_stmt.where(InternshipListingDB.city == params.city)

        if params.work_modality:
            val = params.work_modality.value if hasattr(params.work_modality, 'value') else params.work_modality
            stmt = stmt.where(InternshipListingDB.work_modality == val)
            count_stmt = count_stmt.where(InternshipListingDB.work_modality == val)

        if params.internship_type:
            val = params.internship_type.value if hasattr(params.internship_type, 'value') else params.internship_type
            stmt = stmt.where(InternshipListingDB.internship_type == val)
            count_stmt = count_stmt.where(InternshipListingDB.internship_type == val)

        if params.is_paid is not None:
            stmt = stmt.where(InternshipListingDB.is_paid == params.is_paid)
            count_stmt = count_stmt.where(InternshipListingDB.is_paid == params.is_paid)

        if params.requires_mandatory_letter is not None:
            stmt = stmt.where(
                InternshipListingDB.requires_mandatory_letter == params.requires_mandatory_letter
            )
            count_stmt = count_stmt.where(
                InternshipListingDB.requires_mandatory_letter == params.requires_mandatory_letter
            )

        if params.min_days_per_week_max is not None:
            stmt = stmt.where(
                or_(
                    InternshipListingDB.min_days_per_week <= params.min_days_per_week_max,
                    InternshipListingDB.min_days_per_week.is_(None),
                )
            )
            count_stmt = count_stmt.where(
                or_(
                    InternshipListingDB.min_days_per_week <= params.min_days_per_week_max,
                    InternshipListingDB.min_days_per_week.is_(None),
                )
            )

        if params.posted_after:
            stmt = stmt.where(InternshipListingDB.posted_date >= params.posted_after)
            count_stmt = count_stmt.where(InternshipListingDB.posted_date >= params.posted_after)

        if params.deadline_before:
            stmt = stmt.where(
                or_(
                    InternshipListingDB.application_deadline <= params.deadline_before,
                    InternshipListingDB.application_deadline.is_(None),
                )
            )
            count_stmt = count_stmt.where(
                or_(
                    InternshipListingDB.application_deadline <= params.deadline_before,
                    InternshipListingDB.application_deadline.is_(None),
                )
            )

        # Eligible level filter (JSONB array contains)
        if params.eligible_level:
            val = params.eligible_level.value if hasattr(params.eligible_level, 'value') else params.eligible_level
            level_filter = InternshipListingDB.eligible_levels_json.contains([val])
            stmt = stmt.where(level_filter)
            count_stmt = count_stmt.where(level_filter)

        # Department category filter (JSONB array contains)
        if params.department_category:
            val = params.department_category.value if hasattr(params.department_category, 'value') else params.department_category
            cat_filter = InternshipListingDB.department_categories_json.contains([val])
            stmt = stmt.where(cat_filter)
            count_stmt = count_stmt.where(cat_filter)

        # Department name filter (search in JSONB array)
        if params.department_name:
            dept_filter = cast(InternshipListingDB.eligible_departments_json, String).ilike(
                f"%{params.department_name}%"
            )
            stmt = stmt.where(dept_filter)
            count_stmt = count_stmt.where(dept_filter)

        # Sorting
        if params.sort_by == "posted_date_desc":
            stmt = stmt.order_by(InternshipListingDB.posted_date.desc().nullslast())
        elif params.sort_by == "deadline_asc":
            stmt = stmt.order_by(InternshipListingDB.application_deadline.asc().nullslast())
        elif params.sort_by == "confidence_desc":
            stmt = stmt.order_by(InternshipListingDB.extraction_confidence.desc().nullslast())
        else:
            stmt = stmt.order_by(InternshipListingDB.first_seen_at.desc())

        # Get total count
        total = self.session.execute(count_stmt).scalar() or 0

        # Pagination
        offset = (params.page - 1) * params.page_size
        stmt = stmt.offset(offset).limit(params.page_size)

        listings = list(self.session.execute(stmt).scalars().all())
        return listings, total

    def get_stats(self) -> dict:
        """Get overall statistics about listings."""
        total = self.session.execute(
            select(func.count(InternshipListingDB.id))
        ).scalar() or 0
        by_status = {}
        for status in ListingStatus:
            count = self.session.execute(
                select(func.count(InternshipListingDB.id)).where(
                    InternshipListingDB.status == status.value
                )
            ).scalar() or 0
            by_status[status.value] = count
        return {"total": total, "by_status": by_status}

    def source_job_id_exists(
        self, source_platform: str, source_job_id: str
    ) -> bool:
        """Quick existence check for deduplication."""
        stmt = select(func.count(InternshipListingDB.id)).where(
            and_(
                InternshipListingDB.source_platform == source_platform,
                InternshipListingDB.source_job_id == source_job_id,
            )
        )
        return (self.session.execute(stmt).scalar() or 0) > 0


class DepartmentRepository:
    """Repository for department reference data."""

    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[DepartmentDB]:
        stmt = select(DepartmentDB).order_by(DepartmentDB.category, DepartmentDB.name_tr)
        return list(self.session.execute(stmt).scalars().all())

    def get_by_category(self, category: str) -> list[DepartmentDB]:
        stmt = (
            select(DepartmentDB)
            .where(DepartmentDB.category == category)
            .order_by(DepartmentDB.name_tr)
        )
        return list(self.session.execute(stmt).scalars().all())

    def search(self, query: str) -> list[DepartmentDB]:
        """Search departments by name or alias."""
        stmt = select(DepartmentDB).where(
            or_(
                DepartmentDB.name_tr.ilike(f"%{query}%"),
                DepartmentDB.name_en.ilike(f"%{query}%"),
                cast(DepartmentDB.aliases, String).ilike(f"%{query}%"),
            )
        )
        return list(self.session.execute(stmt).scalars().all())

    def upsert(self, name_tr: str, name_en: str | None, category: str, aliases: list[str] | None) -> DepartmentDB:
        """Insert or update a department."""
        existing = self.session.execute(
            select(DepartmentDB).where(DepartmentDB.name_tr == name_tr)
        ).scalar_one_or_none()
        
        if existing:
            existing.name_en = name_en
            existing.category = category
            existing.aliases = aliases
            return existing
        
        dept = DepartmentDB(
            name_tr=name_tr,
            name_en=name_en,
            category=category,
            aliases=aliases,
        )
        self.session.add(dept)
        self.session.flush()
        return dept
