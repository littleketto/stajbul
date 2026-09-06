from dataclasses import dataclass
from curl_cffi import requests as curl_requests
import logging

logger = logging.getLogger(__name__)

@dataclass
class HttpResponse:
    status_code: int
    text: str
    url: str
    is_blocked: bool = False      # 999 status
    is_rate_limited: bool = False  # 429 status  
    is_auth_wall: bool = False     # Redirect to login
    error: str | None = None

class LinkedInClient:
    BASE_URL = "https://www.linkedin.com"
    SEARCH_ENDPOINT = "/jobs-guest/jobs/api/seeMoreJobPostings/search"
    DETAIL_ENDPOINT = "/jobs-guest/jobs/api/jobPosting/{job_id}"
    
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }
    
    def __init__(self, proxy_url: str | None = None):
        self.proxy_url = proxy_url
        self._proxies = {"https": proxy_url, "http": proxy_url} if proxy_url else None
        
    def _make_request(self, method: str, url: str, params: dict | None = None) -> HttpResponse:
        try:
            resp = curl_requests.request(
                method=method,
                url=url,
                params=params,
                headers=self.HEADERS,
                proxies=self._proxies,
                impersonate="chrome124",
                timeout=15.0,
                allow_redirects=True,
            )
            
            is_auth_wall = "authwall" in resp.url or "login" in resp.url
            is_blocked = resp.status_code == 999
            is_rate_limited = resp.status_code == 429
            
            return HttpResponse(
                status_code=resp.status_code,
                text=resp.text,
                url=resp.url,
                is_blocked=is_blocked,
                is_rate_limited=is_rate_limited,
                is_auth_wall=is_auth_wall,
            )
        except Exception as e:
            logger.error(f"Request failed for {url}: {e}")
            return HttpResponse(
                status_code=0,
                text="",
                url=url,
                error=str(e),
            )
    
    def search_jobs(self, params: dict) -> HttpResponse:
        """Perform a search request to the LinkedIn guest jobs API."""
        url = f"{self.BASE_URL}{self.SEARCH_ENDPOINT}"
        return self._make_request("GET", url, params=params)
    
    def get_job_detail(self, job_id: str) -> HttpResponse:
        """Fetch full details for a specific job posting."""
        url = f"{self.BASE_URL}{self.DETAIL_ENDPOINT.format(job_id=job_id)}"
        return self._make_request("GET", url)
