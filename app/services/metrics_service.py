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
        
        # Scheduler metrics
        self._queue_depth = 0
        self._scheduled_count = 0
        self._total_wait_time_ms = 0.0

        # Batching metrics
        self._active_batches = 0
        self._total_batches_dispatched = 0
        self._total_requests_batched = 0
        self._largest_observed_batch = 0
        self._total_dispatch_delay_ms = 0.0
        self._single_request_fallbacks = 0

        # Cache metrics
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_writes = 0
        self._cache_evictions = 0
        self._cache_lookup_latency_ms = 0.0
        self._cache_write_latency_ms = 0.0

        # Event buffers for Histograms
        self._recent_request_latencies: list[float] = []
        self._recent_scheduler_wait_times: list[float] = []
        self._recent_batch_dispatch_delays: list[float] = []
        self._recent_cache_lookup_latencies: list[float] = []
        self._recent_cache_write_latencies: list[float] = []
        self._recent_provider_latencies: list[tuple[str, str, float]] = []

        # Rate Limiting & Quota Metrics
        self._rate_limit_requests = 0
        self._rate_limit_rejections = 0
        self._quota_violations = 0
        self._tokens_consumed = 0
        self._concurrent_requests = 0
        self._redis_fallback_events = 0
        self._backend_selections: dict[str, int] = {"memory": 0, "redis": 0}

    def record_request(self, latency_ms: float, is_error: bool = False) -> None:
        """Record a single request's latency and error status."""
        with self._lock:
            self._request_count += 1
            self._total_latency += latency_ms
            self._recent_request_latencies.append(latency_ms)
            if is_error:
                self._error_count += 1

    def record_enqueue(self) -> None:
        """Record a request entering the scheduler queue."""
        with self._lock:
            self._queue_depth += 1

    def record_dequeue(self, wait_time_ms: float) -> None:
        """Record a request leaving the scheduler queue."""
        with self._lock:
            if self._queue_depth > 0:
                self._queue_depth -= 1
            self._scheduled_count += 1
            self._total_wait_time_ms += wait_time_ms
            self._recent_scheduler_wait_times.append(wait_time_ms)

    def record_active_batch_added(self) -> None:
        """Record a new active batch created."""
        with self._lock:
            self._active_batches += 1

    def record_active_batch_removed(self) -> None:
        """Record an active batch removed/dispatched."""
        with self._lock:
            if self._active_batches > 0:
                self._active_batches -= 1

    def record_batch_dispatch(self, batch_size: int, delay_ms: float) -> None:
        """Record batch execution metrics."""
        with self._lock:
            self._total_batches_dispatched += 1
            self._total_requests_batched += batch_size
            self._total_dispatch_delay_ms += delay_ms
            self._recent_batch_dispatch_delays.append(delay_ms)
            if batch_size > self._largest_observed_batch:
                self._largest_observed_batch = batch_size

    def record_single_request_fallback(self) -> None:
        """Record when a request could not be batched."""
        with self._lock:
            self._single_request_fallbacks += 1

    def get_queue_depth(self) -> int:
        """Get current scheduler queue depth."""
        with self._lock:
            return self._queue_depth

    def get_average_wait_time(self) -> float:
        """Get average time requests spent waiting in queue."""
        with self._lock:
            if self._scheduled_count == 0:
                return 0.0
            return self._total_wait_time_ms / self._scheduled_count

    def get_average_requests_per_batch(self) -> float:
        with self._lock:
            if self._total_batches_dispatched == 0:
                return 0.0
            return self._total_requests_batched / self._total_batches_dispatched

    def get_average_dispatch_delay(self) -> float:
        with self._lock:
            if self._total_batches_dispatched == 0:
                return 0.0
            return self._total_dispatch_delay_ms / self._total_batches_dispatched

    def get_scheduler_throughput(self) -> int:
        """Get total number of requests processed by scheduler."""
        with self._lock:
            return self._scheduled_count

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

    def record_cache_hit(self) -> None:
        with self._lock:
            self._cache_hits += 1

    def record_cache_miss(self) -> None:
        with self._lock:
            self._cache_misses += 1

    def record_cache_write(self) -> None:
        with self._lock:
            self._cache_writes += 1

    def record_cache_eviction(self) -> None:
        with self._lock:
            self._cache_evictions += 1

    def record_cache_lookup_latency(self, latency_ms: float) -> None:
        with self._lock:
            self._cache_lookup_latency_ms += latency_ms
            self._recent_cache_lookup_latencies.append(latency_ms)

    def record_cache_write_latency(self, latency_ms: float) -> None:
        with self._lock:
            self._cache_write_latency_ms += latency_ms
            self._recent_cache_write_latencies.append(latency_ms)

    def get_cache_hit_ratio(self) -> float:
        with self._lock:
            total_lookups = self._cache_hits + self._cache_misses
            if total_lookups == 0:
                return 0.0
            return self._cache_hits / total_lookups

    def get_metrics_summary(self) -> dict[str, Any]:
        """Return a dictionary summarizing the current metrics."""
        with self._lock:
            return {
                "request_count": self._request_count,
                "error_count": self._error_count,
                "average_latency_ms": self.get_average_latency(),
                "queue_depth": self._queue_depth,
                "average_wait_time_ms": self.get_average_wait_time(),
                "scheduler_throughput": self._scheduled_count,
                "active_batches": self._active_batches,
                "average_requests_per_batch": self.get_average_requests_per_batch(),
                "largest_observed_batch": self._largest_observed_batch,
                "average_dispatch_delay_ms": self.get_average_dispatch_delay(),
                "single_request_fallbacks": self._single_request_fallbacks,
                "cache_hits": self._cache_hits,
                "cache_misses": self._cache_misses,
                "cache_writes": self._cache_writes,
                "cache_evictions": self._cache_evictions,
                "cache_hit_ratio": self.get_cache_hit_ratio(),
                "average_cache_lookup_latency_ms": self._cache_lookup_latency_ms / (self._cache_hits + self._cache_misses) if (self._cache_hits + self._cache_misses) > 0 else 0.0,
                "average_cache_write_latency_ms": self._cache_write_latency_ms / self._cache_writes if self._cache_writes > 0 else 0.0,
                "load_balancer_decisions": getattr(self, "_load_balancer_decisions", 0),
                "requests_per_provider": getattr(self, "_requests_per_provider", {}).copy(),
                "requests_per_instance": getattr(self, "_requests_per_instance", {}).copy(),
                "provider_failures": getattr(self, "_provider_failures", {}).copy(),
                "provider_failovers": getattr(self, "_provider_failovers", {}).copy(),
            }

    # --- Load Balancing Metrics ---
    
    def record_load_balancer_decision(self, provider_id: str, instance_id: str) -> None:
        if not hasattr(self, "_load_balancer_decisions"):
            self._load_balancer_decisions = 0
            self._requests_per_provider = {}
            self._requests_per_instance = {}
            self._provider_failures = {}
            self._provider_failovers = {}
            
        with self._lock:
            self._load_balancer_decisions += 1
            self._requests_per_provider[provider_id] = self._requests_per_provider.get(provider_id, 0) + 1
            self._requests_per_instance[instance_id] = self._requests_per_instance.get(instance_id, 0) + 1
        
    def record_provider_failure(self, provider_id: str, instance_id: str) -> None:
        if not hasattr(self, "_provider_failures"):
            self._provider_failures = {}
            
        key = f"{provider_id}::{instance_id}"
        with self._lock:
            self._provider_failures[key] = self._provider_failures.get(key, 0) + 1
        
    def record_failover(self, provider_id: str) -> None:
        if not hasattr(self, "_provider_failovers"):
            self._provider_failovers = {}
            
        with self._lock:
            self._provider_failovers[provider_id] = self._provider_failovers.get(provider_id, 0) + 1

    def record_provider_latency(self, provider_id: str, instance_id: str, latency_ms: float) -> None:
        with self._lock:
            self._recent_provider_latencies.append((provider_id, instance_id, latency_ms))

    def drain_histograms(self) -> dict[str, list[Any]]:
        """Returns buffered latency events and clears the buffers. Used by Prometheus exporter."""
        with self._lock:
            data = {
                "request_latencies": self._recent_request_latencies,
                "scheduler_wait_times": self._recent_scheduler_wait_times,
                "batch_dispatch_delays": self._recent_batch_dispatch_delays,
                "cache_lookup_latencies": self._recent_cache_lookup_latencies,
                "cache_write_latencies": self._recent_cache_write_latencies,
                "provider_latencies": self._recent_provider_latencies,
            }
            self._recent_request_latencies = []
            self._recent_scheduler_wait_times = []
            self._recent_batch_dispatch_delays = []
            self._recent_cache_lookup_latencies = []
            self._recent_cache_write_latencies = []
            self._recent_provider_latencies = []
            return data

    # --- Limits & Quotas Metrics ---
    
    def record_rate_limit_check(self, allowed: bool) -> None:
        with self._lock:
            self._rate_limit_requests += 1
            if not allowed:
                self._rate_limit_rejections += 1

    def record_quota_violation(self) -> None:
        with self._lock:
            self._quota_violations += 1

    def record_token_consumption(self, total_tokens: int) -> None:
        with self._lock:
            self._tokens_consumed += total_tokens

    def set_concurrent_requests(self, count: int) -> None:
        with self._lock:
            self._concurrent_requests = count

    def record_redis_fallback(self) -> None:
        with self._lock:
            self._redis_fallback_events += 1

    def record_backend_selection(self, backend: str) -> None:
        with self._lock:
            if backend in self._backend_selections:
                self._backend_selections[backend] += 1
            else:
                self._backend_selections[backend] = 1

    def get_limits_summary(self) -> dict[str, Any]:
        with self._lock:
            return {
                "rate_limit_requests": self._rate_limit_requests,
                "rate_limit_rejections": self._rate_limit_rejections,
                "quota_violations": self._quota_violations,
                "tokens_consumed": self._tokens_consumed,
                "concurrent_requests": self._concurrent_requests,
                "redis_fallback_events": self._redis_fallback_events,
                "backend_selections": self._backend_selections.copy(),
            }
