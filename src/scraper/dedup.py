"""Deduplication utilities for scraped job listings."""

import logging
from src.models.schemas import ScrapedJobCard
from src.storage.repositories import ListingRepository

logger = logging.getLogger(__name__)


class DeduplicationFilter:
    """Filters out job cards that already exist in the database."""
    
    def __init__(self, repository: ListingRepository):
        self.repository = repository
    
    def filter_new_cards(
        self,
        cards: list[ScrapedJobCard],
        source_platform: str = "LINKEDIN",
    ) -> tuple[list[ScrapedJobCard], int]:
        """
        Filter a list of scraped job cards, returning only those not yet in the DB.
        Returns (new_cards, duplicate_count).
        """
        new_cards = []
        duplicate_count = 0
        
        for card in cards:
            if self.repository.source_job_id_exists(source_platform, card.job_id):
                duplicate_count += 1
            else:
                new_cards.append(card)
        
        logger.info(
            f"Dedup result: {len(new_cards)} new, {duplicate_count} duplicates "
            f"(out of {len(cards)} total)"
        )
        return new_cards, duplicate_count
