"""Pydantic schemas for LLM structured output, API requests/responses."""

from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from .enums import (
    DepartmentCategory,
    InternshipType,
    ListingStatus,
    SourcePlatform,
    StudentLevel,
    WorkModality,
    WorkSchedule,
)


# ─────────────────────────────────────────────────────────────────────────────
# LLM Structured Output Schema
# This defines what the LLM must extract from job listing descriptions.
# Used directly with Gemini Structured Outputs / OpenAI function calling.
# ─────────────────────────────────────────────────────────────────────────────

class ExtractedInternshipData(BaseModel):
    """Structured data extracted from an internship listing by the LLM."""
    model_config = ConfigDict(use_enum_values=True)

    # ── Core Info ──
    position_title: str = Field(
        ...,
        description="Position title (e.g., 'Yazılım Geliştirme Stajyeri')",
    )
    company_name: str = Field(
        ...,
        description="Company name",
    )

    # ── Internship Type & Format ──
    internship_type: InternshipType = Field(
        default=InternshipType.UNKNOWN,
        description="Internship type: mandatory, voluntary, candidate engineer, co-op, trainee/MT, summer, long-term",
    )
    requires_mandatory_internship_letter: Optional[bool] = Field(
        default=None,
        description="Does the company require a mandatory internship letter from the university (zorunlu staj belgesi)?",
    )
    work_modality: WorkModality = Field(
        default=WorkModality.UNKNOWN,
        description="Work arrangement: on-site, remote, or hybrid",
    )
    work_schedule: WorkSchedule = Field(
        default=WorkSchedule.UNKNOWN,
        description="Full-time or part-time?",
    )

    # ── Eligibility: Class & Department ──
    eligible_levels: list[StudentLevel] = Field(
        default_factory=list,
        description="Eligible student levels (e.g., [3_SINIF, 4_SINIF])",
    )
    eligible_departments: list[str] = Field(
        default_factory=list,
        description="Eligible departments in Turkish full names (e.g., ['Bilgisayar Mühendisliği', 'Yazılım Mühendisliği'])",
    )
    department_categories: list[DepartmentCategory] = Field(
        default_factory=list,
        description="Parent discipline categories (e.g., [MUHENDISLIK, IIBF_ISLETME])",
    )

    # ── Dates & Duration ──
    application_deadline: Optional[date] = Field(
        default=None,
        description="Application deadline (YYYY-MM-DD)",
    )
    start_date: Optional[date] = Field(
        default=None,
        description="Internship start date",
    )
    end_date: Optional[date] = Field(
        default=None,
        description="Internship end date",
    )
    duration_description: Optional[str] = Field(
        default=None,
        description="Duration description (e.g., '20 iş günü', '3 ay', '6 ay+')",
    )

    # ── Location ──
    city: Optional[str] = Field(
        default=None,
        description="City (e.g., İstanbul, Ankara, İzmir)",
    )
    district: Optional[str] = Field(
        default=None,
        description="District / neighborhood (e.g., Maslak, Levent, ODTÜ Teknokent)",
    )

    # ── Working Conditions ──
    min_days_per_week: Optional[int] = Field(
        default=None,
        ge=1,
        le=7,
        description="Minimum required office/work days per week",
    )
    is_paid: Optional[bool] = Field(
        default=None,
        description="Is the internship paid?",
    )
    salary_description: Optional[str] = Field(
        default=None,
        description="Compensation info if available",
    )

    # ── Requirements ──
    required_skills: list[str] = Field(
        default_factory=list,
        description="Required technical/soft skills (e.g., ['Python', 'SQL', 'Excel'])",
    )
    language_requirements: list[str] = Field(
        default_factory=list,
        description="Language requirements (e.g., ['İngilizce - İleri Düzey'])",
    )
    driver_license_required: bool = Field(
        default=False,
        description="Is a driver's license required?",
    )
    travel_required: bool = Field(
        default=False,
        description="Is travel required?",
    )
    military_status_required: bool = Field(
        default=False,
        description="Is military service status relevant? (for male candidates)",
    )

    # ── Summary ──
    summary_tr: str = Field(
        ...,
        max_length=500,
        description="Turkish summary of the listing (2-3 sentences, student perspective)",
    )

    # ── Confidence ──
    extraction_confidence: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Overall confidence score for extracted data (0.0-1.0)",
    )


# ─────────────────────────────────────────────────────────────────────────────
# Scraper Output Schemas
# ─────────────────────────────────────────────────────────────────────────────

class ScrapedJobCard(BaseModel):
    """A job card parsed from LinkedIn search results."""
    job_id: str
    title: str
    company: str
    location: str = ""
    posted_date: Optional[date] = None
    url: str


class ScrapedJobDetail(BaseModel):
    """Full detail of a job posting fetched from LinkedIn."""
    job_id: str
    description_html: str = ""
    description_text: str = ""
    seniority_level: Optional[str] = None
    employment_type: Optional[str] = None
    job_function: Optional[str] = None
    industries: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# Full Listing Schema (DB Record)
# ─────────────────────────────────────────────────────────────────────────────

class InternshipListingSchema(BaseModel):
    """Complete internship listing record — scraper metadata + LLM output."""
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)

    id: Optional[int] = None
    source_platform: SourcePlatform
    source_job_id: str
    source_url: str

    # Raw data from scraper
    raw_title: str
    raw_company: str
    raw_location: str = ""
    raw_description_text: Optional[str] = None
    raw_description_html: Optional[str] = None

    # Status & timestamps
    status: ListingStatus = ListingStatus.RAW
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    posted_date: Optional[date] = None
    enriched_at: Optional[datetime] = None

    # Enriched data (populated after LLM processing)
    enriched_data: Optional[ExtractedInternshipData] = None

    # Denormalized fields for fast filtering
    city: Optional[str] = None
    work_modality: Optional[WorkModality] = None
    work_schedule: Optional[WorkSchedule] = None
    internship_type: Optional[InternshipType] = None
    is_paid: Optional[bool] = None
    requires_mandatory_letter: Optional[bool] = None
    application_deadline: Optional[date] = None
    min_days_per_week: Optional[int] = None
    summary_tr: Optional[str] = None
    extraction_confidence: Optional[float] = None

    # Meta
    scrape_batch_id: Optional[str] = None
    llm_model_used: Optional[str] = None
    llm_token_count: Optional[int] = None


# ─────────────────────────────────────────────────────────────────────────────
# API Filter Schema
# ─────────────────────────────────────────────────────────────────────────────

class ListingFilterParams(BaseModel):
    """Query parameters for filtering internship listings via the API."""
    keyword: Optional[str] = None
    city: Optional[str] = None
    eligible_level: Optional[StudentLevel] = None       # "I am a 3rd year student"
    department_category: Optional[DepartmentCategory] = None
    department_name: Optional[str] = None               # Free-text department search
    work_modality: Optional[WorkModality] = None
    internship_type: Optional[InternshipType] = None
    is_paid: Optional[bool] = None
    requires_mandatory_letter: Optional[bool] = None
    min_days_per_week_max: Optional[int] = None         # "At most X days/week"
    posted_after: Optional[date] = None
    deadline_before: Optional[date] = None

    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = Field(default="posted_date_desc")


class ListingListResponse(BaseModel):
    """Paginated response for listing queries."""
    items: list[InternshipListingSchema]
    total: int
    page: int
    page_size: int
    total_pages: int


class DepartmentSchema(BaseModel):
    """Department reference data."""
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    name_tr: str
    name_en: Optional[str] = None
    category: str
    aliases: list[str] = Field(default_factory=list)
