import logging
from src.models.schemas import ScrapedJobDetail
from .client import LinkedInClient
from .rate_limiter import AdaptiveRateLimiter
from .parser import LinkedInParser

logger = logging.getLogger(__name__)


class DetailWorker:
    """
    Phase 2 worker: fetches full job descriptions for discovered listings.
    Only fetches details for listings that haven't been scraped yet.
    """
    
    def __init__(
        self,
        client: LinkedInClient,
        rate_limiter: AdaptiveRateLimiter,
        parser: LinkedInParser,
    ):
        self.client = client
        self.rate_limiter = rate_limiter
        self.parser = parser
    
    def fetch_detail(self, job_id: str) -> ScrapedJobDetail | None:
        """Fetch and parse details for a single job posting."""
        wait_time = self.rate_limiter.wait()
        logger.debug(f"Waited {wait_time:.1f}s before detail fetch (job_id={job_id})")
        
        response = self.client.get_job_detail(job_id)
        
        if response.is_blocked:
            logger.warning(f"BLOCKED (999) fetching detail for job_id={job_id}")
            self.rate_limiter.report_ban()
            return None
        
        if response.is_rate_limited:
            logger.warning(f"Rate limited (429) fetching detail for job_id={job_id}")
            self.rate_limiter.report_rate_limit()
            return None
        
        if response.status_code != 200:
            logger.error(f"Status {response.status_code} for job_id={job_id}")
            return None
        
        self.rate_limiter.report_success()
        detail = self.parser.parse_job_detail(response.text, job_id)
        
        if not detail.description_text:
            logger.warning(f"Empty description for job_id={job_id}")
            return None
        
        logger.info(f"Fetched detail for job_id={job_id} ({len(detail.description_text)} chars)")
        return detail
    
    def fetch_batch(self, job_ids: list[str]) -> list[ScrapedJobDetail]:
        """Fetch details for a batch of job IDs."""
        results = []
        for i, job_id in enumerate(job_ids):
            logger.info(f"Fetching detail {i+1}/{len(job_ids)}: {job_id}")
            detail = self.fetch_detail(job_id)
            if detail:
                results.append(detail)
        
        logger.info(f"Fetched {len(results)}/{len(job_ids)} job details successfully")
        return results
