from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

@dataclass
class ProxyConfig:
    url: str | None = None
    is_healthy: bool = True
    failure_count: int = 0
    success_count: int = 0

class ProxyManager:
    """Manages proxy rotation. MVP: direct connection (no proxy)."""
    
    def __init__(self, proxy_url: str | None = None):
        if proxy_url:
            self._proxies = [ProxyConfig(url=proxy_url)]
        else:
            self._proxies = [ProxyConfig()]  # Direct connection
        self._current_index = 0
        self._blacklisted: set[str] = set()
    
    def get_next_proxy(self) -> ProxyConfig:
        if not self._proxies:
            return ProxyConfig()
            
        proxy = self._proxies[self._current_index]
        self._current_index = (self._current_index + 1) % len(self._proxies)
        return proxy
    
    def report_success(self, proxy: ProxyConfig) -> None:
        proxy.success_count += 1
        proxy.failure_count = 0
        proxy.is_healthy = True
    
    def report_failure(self, proxy: ProxyConfig, status_code: int) -> None:
        proxy.failure_count += 1
        if proxy.failure_count > 3:
            proxy.is_healthy = False
            if proxy.url:
                self._blacklisted.add(proxy.url)
    
    def get_stats(self) -> dict:
        return {
            "total_proxies": len(self._proxies),
            "healthy": sum(1 for p in self._proxies if p.is_healthy),
            "blacklisted": len(self._blacklisted)
        }
