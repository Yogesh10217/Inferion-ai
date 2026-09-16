"""Performance and Percentile Monitoring Subsystem."""

from __future__ import annotations

import math
import time
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass
class PerformanceMetricsSummary:
    """Summary of component performance metrics."""
    component: str
    count: int
    p50_ms: float
    p95_ms: float
    p99_ms: float
    avg_ms: float
    min_ms: float
    max_ms: float
    error_rate: float
    throughput_per_sec: float
    retry_count: int
    active_concurrency: int


class PerformanceMonitor:
    """Monitors component latencies, error rates, throughput, and percentiles (p50, p95, p99)."""

    def __init__(self) -> None:
        self._latencies: Dict[str, List[float]] = defaultdict(list)
        self._failures: Dict[str, int] = defaultdict(int)
        self._retries: Dict[str, int] = defaultdict(int)
        self._requests: Dict[str, int] = defaultdict(int)
        self._active_concurrency: Dict[str, int] = defaultdict(int)
        self._start_times: Dict[str, float] = defaultdict(time.time)

    def record_latency(self, component: str, latency_ms: float, is_error: bool = False, is_retry: bool = False) -> None:
        """Record an execution duration for a component."""
        self._latencies[component].append(latency_ms)
        self._requests[component] += 1
        if is_error:
            self._failures[component] += 1
        if is_retry:
            self._retries[component] += 1

    def increment_concurrency(self, component: str) -> int:
        """Track active concurrent execution start."""
        self._active_concurrency[component] += 1
        return self._active_concurrency[component]

    def decrement_concurrency(self, component: str) -> int:
        """Track active concurrent execution end."""
        self._active_concurrency[component] = max(0, self._active_concurrency[component] - 1)
        return self._active_concurrency[component]

    def record_throughput(self, component: str, count: int = 1) -> None:
        """Record throughput requests for a component."""
        self._requests[component] += count

    def record_failure(self, component: str, is_retry: bool = False) -> None:
        """Record a component execution failure."""
        self._failures[component] += 1
        if is_retry:
            self._retries[component] += 1

    def calculate_percentiles(self, latencies: List[float]) -> Dict[str, float]:
        """Calculate p50, p95, and p99 percentiles from a list of latencies."""
        if not latencies:
            return {"p50": 0.0, "p95": 0.0, "p99": 0.0, "avg": 0.0, "min": 0.0, "max": 0.0}

        sorted_lat = sorted(latencies)
        n = len(sorted_lat)

        def percentile(p: float) -> float:
            k = (n - 1) * p
            f = math.floor(k)
            c = math.ceil(k)
            if f == c:
                return sorted_lat[int(k)]
            d0 = sorted_lat[int(f)] * (c - k)
            d1 = sorted_lat[int(c)] * (k - f)
            return d0 + d1

        return {
            "p50": round(percentile(0.50), 2),
            "p95": round(percentile(0.95), 2),
            "p99": round(percentile(0.99), 2),
            "avg": round(sum(sorted_lat) / n, 2),
            "min": round(sorted_lat[0], 2),
            "max": round(sorted_lat[-1], 2),
        }

    def get_component_performance(self, component: str) -> PerformanceMetricsSummary:
        """Retrieve aggregated performance metrics for a specific component."""
        latencies = self._latencies.get(component, [])
        stats = self.calculate_percentiles(latencies)
        total_reqs = self._requests.get(component, len(latencies))
        fail_count = self._failures.get(component, 0)
        error_rate = (fail_count / total_reqs) if total_reqs > 0 else 0.0

        start_time = self._start_times.get(component, time.time())
        elapsed = max(1.0, time.time() - start_time)
        throughput = round(total_reqs / elapsed, 2)

        return PerformanceMetricsSummary(
            component=component,
            count=total_reqs,
            p50_ms=stats["p50"],
            p95_ms=stats["p95"],
            p99_ms=stats["p99"],
            avg_ms=stats["avg"],
            min_ms=stats["min"],
            max_ms=stats["max"],
            error_rate=round(error_rate, 4),
            throughput_per_sec=throughput,
            retry_count=self._retries.get(component, 0),
            active_concurrency=self._active_concurrency.get(component, 0),
        )

    def get_all_performance(self) -> Dict[str, Dict[str, Any]]:
        """Get summary across all recorded components."""
        all_components = set(self._latencies.keys()) | set(self._requests.keys())
        result = {}
        for c in all_components:
            summary = self.get_component_performance(c)
            result[c] = {
                "component": summary.component,
                "count": summary.count,
                "p50_ms": summary.p50_ms,
                "p95_ms": summary.p95_ms,
                "p99_ms": summary.p99_ms,
                "avg_ms": summary.avg_ms,
                "min_ms": summary.min_ms,
                "max_ms": summary.max_ms,
                "error_rate": summary.error_rate,
                "throughput_per_sec": summary.throughput_per_sec,
                "retry_count": summary.retry_count,
                "active_concurrency": summary.active_concurrency,
            }
        return result
