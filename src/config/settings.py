from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/staj_platform"
    async_database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/staj_platform"

    # Gemini
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # Scraper
    scraper_base_delay: float = 3.0
    scraper_max_delay: float = 120.0
    scraper_jitter_min: float = 1.0
    scraper_jitter_max: float = 3.0
    scraper_requests_per_minute: int = 10

    # Proxy
    proxy_enabled: bool = False
    proxy_url: str = ""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # Scheduler
    scheduler_enabled: bool = True
    scrape_interval_hours: int = 6


def get_settings() -> Settings:
    return Settings()
