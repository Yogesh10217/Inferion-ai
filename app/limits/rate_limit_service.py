import logging
from typing import Tuple

from app.limits.counter_backend import CounterBackend
from app.limits.exceptions import RateLimitExceededException
from app.services.metrics_service import MetricsService

logger = logging.getLogger(__name__)

class RateLimitService:
    def __init__(self, backend: CounterBackend, metrics: MetricsService, default_strategy: str = "sliding_window"):
        self.backend = backend
        self.metrics = metrics
        self.default_strategy = default_strategy

    async def check_rate_limit(self, scope_id: str, limit: int, window_seconds: int, strategy: str = None) -> None:
        """
        Check rate limit and raise RateLimitExceededException if exceeded.
        scope_id: identifier (e.g., org:123 or api_key:456)
        """
        strategy = strategy or self.default_strategy
        key = f"ratelimit:{strategy}:{scope_id}"
        
        allowed = True
        
        if strategy == "sliding_window":
            allowed, _ = await self.backend.check_and_increment_sliding_window(key, limit, window_seconds)
        elif strategy == "token_bucket":
            allowed, _ = await self.backend.check_and_decrement_token_bucket(key, limit, window_seconds)
        elif strategy == "fixed_window":
            allowed, _ = await self.backend.check_and_increment_fixed_window(key, limit, window_seconds)
        else:
            logger.warning(f"Unknown rate limit strategy: {strategy}, falling back to fixed_window")
            allowed, _ = await self.backend.check_and_increment_fixed_window(key, limit, window_seconds)
            
        self.metrics.record_rate_limit_check(allowed)
        
        if not allowed:
            raise RateLimitExceededException(f"Rate limit exceeded for scope {scope_id}")

    async def acquire_concurrency_lease(self, scope_id: str, limit: int, ttl_seconds: int = 60) -> str:
        """
        Acquire a concurrent execution lease. Raises if exceeded.
        """
        key = f"concurrency:{scope_id}"
        allowed, lease_id = await self.backend.acquire_lease(key, limit, ttl_seconds)
        
        if not allowed:
            self.metrics.record_rate_limit_check(False)
            raise RateLimitExceededException(f"Concurrent request limit exceeded for scope {scope_id}")
            
        return lease_id

    async def release_concurrency_lease(self, scope_id: str, lease_id: str) -> None:
        """Release a previously acquired lease."""
        key = f"concurrency:{scope_id}"
        await self.backend.release_lease(key, lease_id)
