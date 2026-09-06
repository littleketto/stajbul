"""SQLAlchemy ORM models for the Smart Internship Platform."""

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Float,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from .enums import (
    InternshipType,
    ListingStatus,
    SourcePlatform,
    WorkModality,
    WorkSchedule,
)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class InternshipListingDB(Base):
    """Main table storing internship listings with raw + enriched data."""
    __tablename__ = "internship_listings"

    # ── Identity ──
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_platform: Mapped[str] = mapped_column(
        String(32), nullable=False, index=True
    )
    source_job_id: Mapped[str] = mapped_column(String(64), nullable=False)
    source_url: Mapped[str] = mapped_column(String(512), nullable=False)

    # ── Raw Data ──
    raw_title: Mapped[str] = mapped_column(String(512), nullable=False)
    raw_company: Mapped[str] = mapped_column(String(256), nullable=False)
    raw_location: Mapped[str | None] = mapped_column(String(256), nullable=True)
    raw_description_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_description_html: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── Status & Timestamps ──
    status: Mapped[str] = mapped_column(
        String(32), default=ListingStatus.RAW.value, index=True
    )
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    posted_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    enriched_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # ── Enriched Data (full JSON blob from LLM) ──
    enriched_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ── Denormalized Fields for Fast Filtering ──
    city: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    work_modality: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    work_schedule: Mapped[str | None] = mapped_column(String(32), nullable=True)
    internship_type: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    is_paid: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    requires_mandatory_letter: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    application_deadline: Mapped[date | None] = mapped_column(
        Date, nullable=True, index=True
    )
    min_days_per_week: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Denormalized JSON arrays for array-contains queries
    eligible_levels_json: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    department_categories_json: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    eligible_departments_json: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    required_skills_json: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # ── Meta ──
    scrape_batch_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    llm_model_used: Mapped[str | None] = mapped_column(String(64), nullable=True)
    llm_token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    summary_tr: Mapped[str | None] = mapped_column(Text, nullable=True)
    extraction_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    # ── Constraints & Indexes ──
    __table_args__ = (
        UniqueConstraint(
            "source_platform", "source_job_id", name="uq_platform_job_id"
        ),
        Index("ix_city_modality", "city", "work_modality"),
        Index("ix_status_enriched", "status", "enriched_at"),
        Index("ix_posted_deadline", "posted_date", "application_deadline"),
    )

    def __repr__(self) -> str:
        return (
            f"<InternshipListing(id={self.id}, "
            f"title='{self.raw_title[:50]}', "
            f"company='{self.raw_company}', "
            f"status='{self.status}')>"
        )


class DepartmentDB(Base):
    """Reference table for Turkish university departments."""
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name_tr: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    name_en: Mapped[str | None] = mapped_column(String(256), nullable=True)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    aliases: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    def __repr__(self) -> str:
        return f"<Department(name_tr='{self.name_tr}', category='{self.category}')>"
