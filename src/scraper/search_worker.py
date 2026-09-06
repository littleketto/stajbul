import json
import logging
from pathlib import Path
from dataclasses import dataclass

from src.models.schemas import ScrapedJobCard
from .client import LinkedInClient
from .rate_limiter import AdaptiveRateLimiter
from .parser import LinkedInParser

logger = logging.getLogger(__name__)


@dataclass
class SearchQuery:
    """A single search query configuration."""
    id: str
    keywords: str
    geo_id: str
    experience_levels: list[str]
    time_range: str = "r86400"
    sort: str = "DD"
    priority: int = 1


class SearchWorker:
    """
    Phase 1 worker: discovers job cards via LinkedIn's guest search endpoint.
    Paginates through results (25 per page) for each search query.
    """
    MAX_PAGES = 40  # LinkedIn caps at ~1000 results (40 pages × 25)
    PAGE_SIZE = 25
    
    def __init__(
        self,
        client: LinkedInClient,
        rate_limiter: AdaptiveRateLimiter,
        parser: LinkedInParser,
    ):
        self.client = client
        self.rate_limiter = rate_limiter
        self.parser = parser
    
    def load_queries_from_file(self, filepath: str | Path | None = None) -> list[SearchQuery]:
        """Load search queries from data/keywords.json."""
        if filepath is None:
            filepath = Path(__file__).resolve().parent.parent.parent / "data" / "keywords.json"
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        queries = []
        for q in data["search_queries"]:
            for exp_level in q["experience_levels"]:
                queries.append(SearchQuery(
                    id=f"{q['id']}_e{exp_level}",
                    keywords=q["keywords"],
                    geo_id=q["geo_id"],
                    experience_levels=[exp_level],
                    time_range=q.get("time_range", "r86400"),
                    sort=q.get("sort", "DD"),
                    priority=q.get("priority", 1),
                ))
        # Sort by priority
        queries.sort(key=lambda q: q.priority)
        return queries
    
    def run_search(self, query: SearchQuery) -> list[ScrapedJobCard]:
        """
        Execute a single search query, paginating through all result pages.
        Returns all discovered job cards.
        """
        all_cards: list[ScrapedJobCard] = []
        
        for page in range(self.MAX_PAGES):
            start = page * self.PAGE_SIZE
            params = {
                "keywords": query.keywords,
                "geoId": query.geo_id,
                "f_E": ",".join(query.experience_levels),
                "f_TPR": query.time_range,
                "sortBy": query.sort,
                "start": str(start),
            }
            
            # Rate limit
            wait_time = self.rate_limiter.wait()
            logger.debug(f"Waited {wait_time:.1f}s before request (query={query.id}, page={page})")
            
            # Make request
            response = self.client.search_jobs(params)
            
            if response.is_blocked:
                logger.warning(f"BLOCKED (999) on query={query.id}, page={page}")
                self.rate_limiter.report_ban()
                break
            
            if response.is_rate_limited:
                logger.warning(f"Rate limited (429) on query={query.id}, page={page}")
                self.rate_limiter.report_rate_limit()
                continue  # Retry after backoff on next iteration
            
            if response.status_code != 200:
                logger.error(f"Unexpected status {response.status_code} on query={query.id}")
                break
            
            # Parse results
            cards = self.parser.parse_search_results(response.text)
            self.rate_limiter.report_success()
            
            if not cards:
                logger.info(f"No more results for query={query.id} at page={page}")
                break
            
            all_cards.extend(cards)
            logger.info(f"Query={query.id} page={page}: found {len(cards)} cards (total: {len(all_cards)})")
        
        return all_cards
    
    def run_all_queries(self, queries: list[SearchQuery] | None = None) -> list[ScrapedJobCard]:
        """Run all search queries and return deduplicated job cards."""
        if queries is None:
            queries = self.load_queries_from_file()
        
        all_cards: list[ScrapedJobCard] = []
        seen_ids: set[str] = set()
        
        for query in queries:
            logger.info(f"Starting search: {query.id} (keywords='{query.keywords}')")
            cards = self.run_search(query)
            
            for card in cards:
                if card.job_id not in seen_ids:
                    seen_ids.add(card.job_id)
                    all_cards.append(card)
        
        logger.info(f"Total unique cards discovered: {len(all_cards)}")
        return all_cards
