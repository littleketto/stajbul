# Akıllı Staj ve Kariyer Fırsatları Platformu

Akıllı Staj ve Kariyer Fırsatları Platformu, Türkiye'deki öğrenciler ve yeni mezunlar için staj ve kariyer fırsatlarını tek bir noktada toplayan, akıllı eşleştirme ve yapay zeka destekli analiz sunan bir platformdur. 

## Tech Stack
- Python 3.12
- FastAPI
- SQLAlchemy (Async)
- PostgreSQL
- Pydantic
- Google GenAI (Gemini)
- APScheduler
- BeautifulSoup4 / curl-cffi

## Quick Start
1. Clone the repository and install dependencies using `uv`:
   ```bash
   uv sync
   ```
2. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
3. Set up the Database (ensure PostgreSQL is running and database `staj_platform` exists).
4. Run the API:
   ```bash
   uv run staj api
   ```

## Directory Structure
- `src/api`: FastAPI routes and application setup
- `src/cli`: Command Line Interface tools
- `src/config`: Application configuration and settings
- `src/enrichment`: Data enrichment and GenAI integration
- `src/models`: Database models and Pydantic schemas
- `src/scraper`: Web scrapers for opportunities
- `src/storage`: Database access and CRUD operations
- `tests`: Test suites
