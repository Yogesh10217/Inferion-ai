from abc import ABC, abstractmethod
from typing import Tuple


class CounterBackend(ABC):
    """Abstract interface for atomic rate limit and concurrency primitives."""

    @abstractmethod
    async def check_and_increment_sliding_window(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Evaluate a sliding window rate limit.
        Returns (is_allowed, remaining).
        """

    @abstractmethod
    async def check_and_decrement_token_bucket(self, key: str, capacity: int, refill_time_seconds: int) -> Tuple[bool, int]:
        """
        Evaluate a token bucket rate limit. Refill rate is capacity / refill_time_seconds.
        Returns (is_allowed, remaining).
        """

    @abstractmethod
    async def check_and_increment_fixed_window(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        """
        Evaluate a fixed window rate limit.
        Returns (is_allowed, remaining).
        """

    @abstractmethod
    async def acquire_lease(self, scope_key: str, limit: int, ttl_seconds: int) -> Tuple[bool, str]:
        """
        Acquire a concurrent execution lease for a given scope.
        Returns (is_allowed, lease_id).
        """

    @abstractmethod
    async def release_lease(self, scope_key: str, lease_id: str) -> None:
        """
        Release a previously acquired concurrent execution lease.
        """
