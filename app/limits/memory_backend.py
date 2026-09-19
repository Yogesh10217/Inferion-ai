import asyncio
import time
import uuid
from typing import Dict, List, Tuple

from app.limits.counter_backend import CounterBackend


class MemoryCounterBackend(CounterBackend):
    """
    In-memory rate limiting and lease tracking using asyncio locks.
    Used for local development or as a fallback circuit-breaker for Redis.
    """

    def __init__(self):
        self._lock = asyncio.Lock()

        # Data structures for limits
        self._sliding_windows: Dict[str, List[float]] = {}
        self._token_buckets: Dict[str, Tuple[float, float]] = {}  # key -> (tokens, last_refreshed)
        self._fixed_windows: Dict[str, Tuple[int, float]] = {}  # key -> (count, expires_at)

        # Leases: key -> {lease_id: expires_at}
        self._leases: Dict[str, Dict[str, float]] = {}

    def _now(self) -> float:
        return time.time()

    async def check_and_increment_sliding_window(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        now = self._now()
        async with self._lock:
            if key not in self._sliding_windows:
                self._sliding_windows[key] = []

            # Clean up old timestamps
            self._sliding_windows[key] = [t for t in self._sliding_windows[key] if now - t <= window_seconds]

            count = len(self._sliding_windows[key])
            if count < limit:
                self._sliding_windows[key].append(now)
                return True, limit - count - 1
            return False, 0

    async def check_and_decrement_token_bucket(
        self, key: str, capacity: int, refill_time_seconds: int
    ) -> Tuple[bool, int]:
        now = self._now()
        refill_rate = capacity / refill_time_seconds

        async with self._lock:
            if key not in self._token_buckets:
                self._token_buckets[key] = (float(capacity), now)

            last_tokens, last_refreshed = self._token_buckets[key]

            delta = max(0.0, now - last_refreshed)
            filled_tokens = min(float(capacity), last_tokens + (delta * refill_rate))

            if filled_tokens >= 1.0:
                new_tokens = filled_tokens - 1.0
                self._token_buckets[key] = (new_tokens, now)
                return True, int(new_tokens)
            else:
                self._token_buckets[key] = (filled_tokens, now)
                return False, int(filled_tokens)

    async def check_and_increment_fixed_window(self, key: str, limit: int, window_seconds: int) -> Tuple[bool, int]:
        now = self._now()
        async with self._lock:
            if key in self._fixed_windows:
                count, expires_at = self._fixed_windows[key]
                if now > expires_at:
                    self._fixed_windows[key] = (1, now + window_seconds)
                    return True, limit - 1
                elif count < limit:
                    self._fixed_windows[key] = (count + 1, expires_at)
                    return True, limit - count - 1
                else:
                    return False, 0
            else:
                self._fixed_windows[key] = (1, now + window_seconds)
                return True, limit - 1

    async def acquire_lease(self, scope_key: str, limit: int, ttl_seconds: int) -> Tuple[bool, str]:
        now = self._now()
        lease_id = str(uuid.uuid4())

        async with self._lock:
            if scope_key not in self._leases:
                self._leases[scope_key] = {}

            # Clean expired
            active_leases = {lid: expires for lid, expires in self._leases[scope_key].items() if expires > now}

            if len(active_leases) < limit:
                active_leases[lease_id] = now + ttl_seconds
                self._leases[scope_key] = active_leases
                return True, lease_id

            self._leases[scope_key] = active_leases
            return False, ""

    async def release_lease(self, scope_key: str, lease_id: str) -> None:
        async with self._lock:
            if scope_key in self._leases and lease_id in self._leases[scope_key]:
                del self._leases[scope_key][lease_id]
