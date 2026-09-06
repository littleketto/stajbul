"""Domain enums for the Smart Internship Platform."""

from enum import Enum


class InternshipType(str, Enum):
    """Type of internship program."""
    MANDATORY = "ZORUNLU"                    # Zorunlu staj (SGK covered by university)
    VOLUNTARY = "GONULLU"                    # Gönüllü staj
    CANDIDATE_ENGINEER = "ADAY_MUHENDIS"     # Aday mühendis programı
    CO_OP = "CO_OP"                          # Uygulamalı eğitim (7+1, 3+1)
    TRAINEE = "TRAINEE_MT"                   # Genç yetenek / MT programı
    SUMMER = "YAZ_STAJI"                     # Short-term summer internship
    LONG_TERM = "UZUN_DONEM"                 # Long-term internship
    UNKNOWN = "BILINMIYOR"


class WorkModality(str, Enum):
    """Work arrangement model."""
    ON_SITE = "OFISTE"
    REMOTE = "UZAKTAN"
    HYBRID = "HIBRIT"
    UNKNOWN = "BILINMIYOR"


class WorkSchedule(str, Enum):
    """Work time commitment."""
    FULL_TIME = "TAM_ZAMANLI"      # 5 days/week
    PART_TIME = "YARI_ZAMANLI"     # 2-3 days/week
    FLEXIBLE = "ESNEK"             # Flexible hours/days
    UNKNOWN = "BILINMIYOR"


class StudentLevel(str, Enum):
    """Student academic year/level."""
    PREP = "HAZIRLIK"
    FRESHMAN = "1_SINIF"
    SOPHOMORE = "2_SINIF"
    JUNIOR = "3_SINIF"
    SENIOR = "4_SINIF"
    GRADUATE = "YENI_MEZUN"
    MASTERS = "YUKSEK_LISANS"
    VOCATIONAL = "ON_LISANS"       # MYO / Associate degree


class DepartmentCategory(str, Enum):
    """Parent discipline category for departments."""
    ENGINEERING = "MUHENDISLIK"
    BUSINESS = "IIBF_ISLETME"
    NATURAL_SCIENCES = "FEN_BILIMLERI"
    DESIGN_MEDIA = "TASARIM_MEDYA"
    SOCIAL_SCIENCES = "SOSYAL_BILIMLER"
    HEALTH = "SAGLIK"
    LAW = "HUKUK"
    OTHER = "DIGER"


class ListingStatus(str, Enum):
    """Processing status of a listing."""
    RAW = "RAW"                    # Raw data collected, no description yet
    SCRAPED = "SCRAPED"            # Description fetched
    ENRICHED = "ENRICHED"          # Processed by LLM
    FAILED = "FAILED"              # Processing failed
    EXPIRED = "EXPIRED"            # Listing expired
    DUPLICATE = "DUPLICATE"        # Duplicate listing


class SourcePlatform(str, Enum):
    """Source platform where the listing was found."""
    LINKEDIN = "LINKEDIN"
    GREENHOUSE = "GREENHOUSE"      # Future
    LEVER = "LEVER"                # Future
    KARIYER_NET = "KARIYER_NET"    # Future
    MANUAL = "MANUAL"              # Manually added
