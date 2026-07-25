import time
import asyncio
from dataclasses import dataclass
from typing import Optional


@dataclass
class HealthStatus:
    is_healthy: bool
    consecutive_failures: int
    consecutive_successes: int
    active_requests: int
    rolling_latency_ms: float
    last_failure_time: Optional[float]
    last_success_time: Optional[float]


class ProviderHealthMonitor:
    """Tracks the health and performance of a provider instance."""

    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_time_s: float = 30.0,
        latency_window_size: int = 10,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_time_s = recovery_time_s
        self.latency_window_size = latency_window_size

        self._consecutive_failures = 0
        self._consecutive_successes = 0
        self._active_requests = 0
        self._last_failure_time: Optional[float] = None
        self._last_success_time: Optional[float] = None

        # Simple rolling average
        self._latencies: list[float] = []
        
        self._lock = asyncio.Lock()

    def is_healthy(self) -> bool:
        """Determine if the provider is currently healthy and eligible for traffic."""
        # Not async to allow fast sync checks in routing, but we can't use Lock here easily.
        # Since GIL protects simple reads/writes, and this is just returning a bool, we approximate.
        if self._consecutive_failures < self.failure_threshold:
            return True
            
        # In cooldown/recovery period
        if self._last_failure_time is not None:
            if time.time() - self._last_failure_time > self.recovery_time_s:
                # Cooldown expired, allow retry
                return True
                
        return False

    async def record_active(self) -> None:
        """Record that a request has started."""
        async with self._lock:
            self._active_requests += 1

    async def record_success(self, latency_ms: float) -> None:
        """Record a successful request completion with latency."""
        async with self._lock:
            self._active_requests = max(0, self._active_requests - 1)
            self._consecutive_failures = 0
            self._consecutive_successes += 1
            self._last_success_time = time.time()
            
            self._latencies.append(latency_ms)
            if len(self._latencies) > self.latency_window_size:
                self._latencies.pop(0)

    async def record_failure(self) -> None:
        """Record a failed request."""
        async with self._lock:
            self._active_requests = max(0, self._active_requests - 1)
            self._consecutive_failures += 1
            self._consecutive_successes = 0
            self._last_failure_time = time.time()

    def get_status(self) -> HealthStatus:
        """Get a snapshot of the current health status."""
        rolling_latency = sum(self._latencies) / len(self._latencies) if self._latencies else 0.0
        return HealthStatus(
            is_healthy=self.is_healthy(),
            consecutive_failures=self._consecutive_failures,
            consecutive_successes=self._consecutive_successes,
            active_requests=self._active_requests,
            rolling_latency_ms=rolling_latency,
            last_failure_time=self._last_failure_time,
            last_success_time=self._last_success_time,
        )
