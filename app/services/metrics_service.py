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

    def record_request(self, latency_ms: float, is_error: bool = False) -> None:
        """Record a single request's latency and error status."""
        with self._lock:
            self._request_count += 1
            self._total_latency += latency_ms
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
