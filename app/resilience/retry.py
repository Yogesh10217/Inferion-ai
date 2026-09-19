"""Retry Manager with Exponential Backoff, Full Jitter & Token Retry Budget."""

import asyncio
import logging
import random
import time
from typing import Any, Callable, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RetryPolicy(BaseModel):
    """Configuration rules for retrying failed operations."""

    max_attempts: int = 3
    initial_interval_seconds: float = 0.5
    max_interval_seconds: float = 5.0
    backoff_multiplier: float = 2.0
    use_jitter: bool = True
    retryable_exceptions: List[str] = Field(
        default_factory=lambda: [
            "TimeoutError",
            "ConnectionError",
            "ProviderError",
            "HTTPError",
            "RateLimitExceededError",
        ]
    )


class RetryBudget:
    """Token bucket retry budget preventing retry storms during systemic outages."""

    def __init__(self, max_tokens: int = 100, refill_rate_per_sec: float = 10.0) -> None:
        self.max_tokens = max_tokens
        self.tokens = float(max_tokens)
        self.refill_rate = refill_rate_per_sec
        try:
            loop = asyncio.get_running_loop()
            self.last_refill = loop.time()
        except RuntimeError:
            self.last_refill = time.time()

    def can_retry(self) -> bool:
        try:
            loop = asyncio.get_running_loop()
            now = loop.time()
        except RuntimeError:
            now = time.time()

        if self.last_refill > 0:
            elapsed = now - self.last_refill
            self.tokens = min(float(self.max_tokens), self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False


class RetryManager:
    """Executes callables with configurable exponential backoff, jitter, and retry budget protection."""

    def __init__(self, global_budget: Optional[RetryBudget] = None) -> None:
        self.global_budget = global_budget or RetryBudget()

    def is_retryable(self, exc: Exception, policy: RetryPolicy) -> bool:
        exc_type = type(exc).__name__
        if any(name in exc_type for name in policy.retryable_exceptions):
            return True
        return False

    def calculate_delay(self, attempt: int, policy: RetryPolicy) -> float:
        delay = policy.initial_interval_seconds * (policy.backoff_multiplier ** (attempt - 1))
        delay = min(delay, policy.max_interval_seconds)
        if policy.use_jitter:
            delay = random.uniform(0.5 * delay, 1.5 * delay)
        return delay

    async def execute_async(self, func: Callable, policy: Optional[RetryPolicy] = None, *args, **kwargs) -> Any:
        pol = policy or RetryPolicy()
        last_exc: Optional[Exception] = None

        for attempt in range(1, pol.max_attempts + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as exc:
                last_exc = exc
                if attempt >= pol.max_attempts or not self.is_retryable(exc, pol):
                    raise exc

                if not self.global_budget.can_retry():
                    logger.warning("[RETRY BUDGET EXHAUSTED] Suppressing further retries to prevent retry storm")
                    raise exc

                delay = self.calculate_delay(attempt, pol)
                logger.info(
                    f"[RETRY] Attempt {attempt}/{pol.max_attempts} failed with {type(exc).__name__}. Retrying in {delay:.2f}s..."
                )
                await asyncio.sleep(delay)

        if last_exc:
            raise last_exc
