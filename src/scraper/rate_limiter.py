import random
import time
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class RateLimiterConfig:
    base_delay: float = 3.0
    jitter_min: float = 1.0
    jitter_max: float = 3.0
    max_delay: float = 120.0
    backoff_multiplier: float = 2.0
    cooldown_after_ban: float = 300.0
    recovery_threshold: int = 3  # Successful requests before reducing delay

class AdaptiveRateLimiter:
    def __init__(self, config: RateLimiterConfig | None = None):
        self.config = config or RateLimiterConfig()
        self._current_delay = self.config.base_delay
        self._consecutive_successes = 0
        self._last_request_time = 0.0
    
    def wait(self) -> float:
        """Block until it's safe to make the next request. Returns actual wait time."""
        now = time.time()
        time_since_last = now - self._last_request_time
        
        delay = self._get_jittered_delay()
        
        if time_since_last < delay:
            wait_time = delay - time_since_last
            time.sleep(wait_time)
            self._last_request_time = time.time()
            return wait_time
            
        self._last_request_time = now
        return 0.0
    
    def report_success(self) -> None:
        """Report a successful request. May decrease delay."""
        self._consecutive_successes += 1
        if self._consecutive_successes >= self.config.recovery_threshold:
            self._current_delay = max(self.config.base_delay, self._current_delay / self.config.backoff_multiplier)
            self._consecutive_successes = 0
            logger.debug(f"Rate limiter recovered. Current delay: {self._current_delay:.1f}s")
    
    def report_rate_limit(self) -> None:
        """Report a 429 response. Increases delay exponentially."""
        self._consecutive_successes = 0
        self._current_delay = min(self.config.max_delay, self._current_delay * self.config.backoff_multiplier)
        logger.warning(f"Rate limit hit. Increased delay to {self._current_delay:.1f}s")
        time.sleep(self._current_delay) # backoff immediately
    
    def report_ban(self) -> None:
        """Report a 999 response. Triggers long cooldown."""
        self._consecutive_successes = 0
        self._current_delay = self.config.max_delay
        logger.warning(f"IP Banned. Cooling down for {self.config.cooldown_after_ban}s")
        time.sleep(self.config.cooldown_after_ban)
    
    def _get_jittered_delay(self) -> float:
        """Get current delay with random jitter added."""
        return self._current_delay + random.uniform(self.config.jitter_min, self.config.jitter_max)
