"""CLI commands for the Smart Internship Platform."""

import logging
import sys
import uuid
from datetime import datetime

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.config.settings import get_settings
from src.storage.engine import get_engine, init_db, get_db_session
from src.storage.repositories import ListingRepository, DepartmentRepository
from src.models.enums import SourcePlatform, ListingStatus

console = Console()

# Configure logging
def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose/debug logging")
def cli(verbose: bool):
    """Akıllı Staj Platformu - CLI Management Tool"""
    setup_logging(verbose)


@cli.command()
def init():
    """Initialize the database and create all tables."""
    console.print("[bold blue]Initializing database...[/bold blue]")
    try:
        engine = get_engine()
        init_db(engine)
        console.print("[bold green]✓ Database tables created successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red]✗ Database initialization failed: {e}[/bold red]")
        sys.exit(1)


@cli.command()
def seed():
    """Seed the departments reference table from departments.json."""
    from scripts.seed_departments import seed_departments
    console.print("[bold blue]Seeding departments...[/bold blue]")
    try:
        seed_departments()
        console.print("[bold green]✓ Departments seeded successfully![/bold green]")
    except Exception as e:
        console.print(f"[bold red]✗ Seeding failed: {e}[/bold red]")
        sys.exit(1)


@cli.command()
@click.option("--limit", "-l", default=None, type=int, help="Max search queries to run")
def scrape(limit: int | None):
    """Run the LinkedIn scraper (Phase 1: Discovery + Phase 2: Detail)."""
    from src.scraper.client import LinkedInClient
    from src.scraper.rate_limiter import AdaptiveRateLimiter, RateLimiterConfig
    from src.scraper.parser import LinkedInParser
    from src.scraper.search_worker import SearchWorker
    from src.scraper.detail_worker import DetailWorker
    
    settings = get_settings()
    batch_id = f"batch_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    console.print(f"[bold blue]Starting scrape cycle (batch: {batch_id})...[/bold blue]")
    
    # Initialize components
    proxy_url = settings.proxy_url if settings.proxy_enabled else None
    client = LinkedInClient(proxy_url=proxy_url)
    rate_config = RateLimiterConfig(
        base_delay=settings.scraper_base_delay,
        jitter_min=settings.scraper_jitter_min,
        jitter_max=settings.scraper_jitter_max,
        max_delay=settings.scraper_max_delay,
    )
    rate_limiter = AdaptiveRateLimiter(config=rate_config)
    parser = LinkedInParser()
    
    # Phase 1: Discovery
    console.print("\n[bold yellow]Phase 1: Job Discovery[/bold yellow]")
    search_worker = SearchWorker(client, rate_limiter, parser)
    queries = search_worker.load_queries_from_file()
    if limit:
        queries = queries[:limit]
    
    all_cards = search_worker.run_all_queries(queries)
    console.print(f"  Found {len(all_cards)} unique job cards")
    
    # Save to DB
    engine = get_engine()
    init_db(engine)  # Ensure tables exist
    
    new_count = 0
    with get_db_session(engine) as session:
        repo = ListingRepository(session)
        for card in all_cards:
            _, is_new = repo.upsert_from_job_card(
                card=card,
                source_platform=SourcePlatform.LINKEDIN,
                batch_id=batch_id,
            )
            if is_new:
                new_count += 1
    
    console.print(f"  [green]✓ {new_count} new listings saved, {len(all_cards) - new_count} duplicates skipped[/green]")
    
    # Phase 2: Detail Fetching
    console.print("\n[bold yellow]Phase 2: Detail Fetching[/bold yellow]")
    detail_worker = DetailWorker(client, rate_limiter, parser)
    
    with get_db_session(engine) as session:
        repo = ListingRepository(session)
        raw_listings = repo.get_raw_listings(limit=200)
        console.print(f"  {len(raw_listings)} listings need detail fetching")
        
        fetched = 0
        for listing in raw_listings:
            detail = detail_worker.fetch_detail(listing.source_job_id)
            if detail:
                repo.update_with_detail(
                    source_job_id=listing.source_job_id,
                    description_text=detail.description_text,
                    description_html=detail.description_html,
                )
                fetched += 1
    
    console.print(f"  [green]✓ {fetched} job details fetched[/green]")


@cli.command()
@click.option("--limit", "-l", default=50, type=int, help="Max listings to enrich")
def enrich(limit: int):
    """Run AI enrichment on scraped listings using Gemini."""
    from src.enrichment.text_cleaner import TextCleaner
    from src.enrichment.llm_extractor import LLMExtractor
    from src.enrichment.validators import DataValidator
    
    console.print("[bold blue]Starting AI enrichment...[/bold blue]")
    
    engine = get_engine()
    cleaner = TextCleaner()
    
    try:
        extractor = LLMExtractor()
    except ValueError as e:
        console.print(f"[bold red]✗ {e}[/bold red]")
        sys.exit(1)
    
    validator = DataValidator()
    
    with get_db_session(engine) as session:
        repo = ListingRepository(session)
        scraped_listings = repo.get_scraped_listings(limit=limit)
        console.print(f"  {len(scraped_listings)} listings to enrich")
        
        success = 0
        failed = 0
        total_tokens = 0
        
        for i, listing in enumerate(scraped_listings):
            console.print(
                f"  [{i+1}/{len(scraped_listings)}] Processing: {listing.raw_title[:60]}..."
            )
            
            # Clean text
            cleaned = cleaner.prepare_for_llm(
                html=listing.raw_description_html,
                plain_text=listing.raw_description_text,
            )
            
            if not cleaned:
                repo.mark_failed(listing.id, "Empty description after cleaning")
                failed += 1
                continue
            
            # Extract with LLM
            posted = str(listing.posted_date) if listing.posted_date else None
            extracted, metadata = extractor.extract_with_retry(
                title=listing.raw_title,
                company=listing.raw_company,
                location=listing.raw_location or "",
                description_text=cleaned,
                posted_date=posted,
            )
            
            if extracted:
                # Validate and normalize
                extracted = validator.validate_and_normalize(extracted)
                
                # Save to DB
                repo.update_with_enrichment(
                    listing_id=listing.id,
                    enriched=extracted,
                    model_used=metadata.get("model_used", "unknown"),
                    token_count=metadata.get("token_count"),
                )
                success += 1
                if metadata.get("token_count"):
                    total_tokens += metadata["token_count"]
            else:
                repo.mark_failed(listing.id, metadata.get("error", "Unknown error"))
                failed += 1
        
        console.print(f"\n  [green]✓ Enriched: {success}[/green]")
        console.print(f"  [red]✗ Failed: {failed}[/red]")
        console.print(f"  Tokens used: {total_tokens:,}")


@cli.command()
def stats():
    """Show database statistics."""
    engine = get_engine()
    with get_db_session(engine) as session:
        repo = ListingRepository(session)
        stats_data = repo.get_stats()
    
    table = Table(title="Platform Statistics")
    table.add_column("Status", style="cyan")
    table.add_column("Count", justify="right", style="green")
    
    for status, count in stats_data["by_status"].items():
        table.add_row(status, str(count))
    
    table.add_row("─" * 15, "─" * 5, style="dim")
    table.add_row("TOTAL", str(stats_data["total"]), style="bold")
    
    console.print(table)


@cli.command()
@click.option("--host", default=None, help="API host")
@click.option("--port", default=None, type=int, help="API port")
def serve(host: str | None, port: int | None):
    """Start the FastAPI server."""
    import uvicorn
    settings = get_settings()
    uvicorn.run(
        "src.api.app:app",
        host=host or settings.api_host,
        port=port or settings.api_port,
        reload=settings.api_reload,
    )


@cli.command()
@click.option("--limit", "-l", default=None, type=int, help="Max queries")
def pipeline(limit: int | None):
    """Run the full pipeline: scrape → enrich."""
    console.print("[bold magenta]Running full pipeline...[/bold magenta]\n")
    
    # Import Click context to invoke sub-commands
    ctx = click.get_current_context()
    ctx.invoke(scrape, limit=limit)
    console.print("")
    ctx.invoke(enrich, limit=200)
    
    console.print("\n[bold magenta]Pipeline complete![/bold magenta]")
    ctx.invoke(stats)


if __name__ == "__main__":
    cli()
