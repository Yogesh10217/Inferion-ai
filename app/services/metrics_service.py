from __future__ import annotations

from threading import RLock
from typing import Any

class MetricsService:
    """Thread-safe service to track application metrics like request count, errors, and latencies."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._request_count = 0
        self._error_count = 0
        self._total_latency = 0.0

    def record_request(self, latency_ms: float, is_error: bool = False) -> None:
        """Record a single request's latency and error status."""
        with self._lock:
            self._request_count += 1
            self._total_latency += latency_ms
            if is_error:
                self._error_count += 1

    def get_request_count(self) -> int:
        """Get the total request count."""
        with self._lock:
            return self._request_count

    def get_error_count(self) -> int:
        """Get the total error count."""
        with self._lock:
            return self._error_count

    def get_average_latency(self) -> float:
        """Get average request latency in milliseconds."""
        with self._lock:
            if self._request_count == 0:
                return 0.0
            return self._total_latency / self._request_count

    def get_metrics_summary(self) -> dict[str, Any]:
        """Return a dictionary summarizing the current metrics."""
        with self._lock:
            return {
                "request_count": self._request_count,
                "error_count": self._error_count,
                "average_latency_ms": self.get_average_latency(),
            }
