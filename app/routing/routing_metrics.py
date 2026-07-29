import time
import threading
from typing import Dict, Any, Optional
from prometheus_client import Counter, Histogram, Gauge

# Singleton / Global Prometheus metrics for routing
ROUTING_DECISIONS_TOTAL = Counter(
    "llm_engine_routing_decisions_total",
    "Total number of routing decisions made",
    ["policy", "selected_provider"],
)
ROUTING_FAILURES_TOTAL = Counter(
    "llm_engine_routing_failures_total",
    "Total number of routing decision failures",
    ["reason"],
)
ROUTING_DURATION_SECONDS = Histogram(
    "llm_engine_routing_duration_seconds",
    "Histogram of routing decision latency in seconds",
    buckets=(0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
)
ROUTING_CACHE_HITS = Counter(
    "llm_engine_routing_cache_hits_total",
    "Total number of routing cache hits",
)
ROUTING_CACHE_MISSES = Counter(
    "llm_engine_routing_cache_misses_total",
    "Total number of routing cache misses",
)
PROVIDER_SELECTION_TOTAL = Counter(
    "llm_engine_provider_selection_total",
    "Total provider selections by routing engine",
    ["provider_id"],
)


class ProviderStats:
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.total_latency_ms = 0.0
        self.last_latency_ms = 0.0
        self.avg_latency_ms = 0.0
        self.estimated_cost_per_1k = 0.002  # Default baseline cost

    def record_success(self, latency_ms: float):
        self.total_requests += 1
        self.successful_requests += 1
        self.total_latency_ms += latency_ms
        self.last_latency_ms = latency_ms
        self.avg_latency_ms = self.total_latency_ms / self.successful_requests

    def record_failure(self):
        self.total_requests += 1
        self.failed_requests += 1

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "avg_latency_ms": round(self.avg_latency_ms, 2),
            "last_latency_ms": round(self.last_latency_ms, 2),
            "success_rate": round(self.success_rate, 4),
            "estimated_cost_per_1k": self.estimated_cost_per_1k,
        }


class RoutingMetrics:
    """Real-time, in-memory tracking of provider health and routing metrics."""

    def __init__(self):
        self._lock = threading.RLock()
        self._provider_stats: Dict[str, ProviderStats] = {}

    def _get_or_create_stats(self, provider_id: str) -> ProviderStats:
        if provider_id not in self._provider_stats:
            self._provider_stats[provider_id] = ProviderStats()
        return self._provider_stats[provider_id]

    def record_success(self, provider_id: str, latency_ms: float):
        with self._lock:
            stats = self._get_or_create_stats(provider_id)
            stats.record_success(latency_ms)

    def record_failure(self, provider_id: str):
        with self._lock:
            stats = self._get_or_create_stats(provider_id)
            stats.record_failure()

    def set_provider_cost(self, provider_id: str, cost_per_1k: float):
        with self._lock:
            stats = self._get_or_create_stats(provider_id)
            stats.estimated_cost_per_1k = cost_per_1k

    def get_provider_stats(self, provider_id: str) -> Dict[str, Any]:
        with self._lock:
            stats = self._provider_stats.get(provider_id)
            if not stats:
                return ProviderStats().to_dict()
            return stats.to_dict()

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        with self._lock:
            return {p: stats.to_dict() for p, stats in self._provider_stats.items()}

    # --- Prometheus Hook Wrappers ---
    def observe_decision(self, policy: str, selected_provider: str, duration_sec: float):
        ROUTING_DECISIONS_TOTAL.labels(policy=policy, selected_provider=selected_provider).inc()
        ROUTING_DURATION_SECONDS.observe(duration_sec)
        PROVIDER_SELECTION_TOTAL.labels(provider_id=selected_provider).inc()

    def observe_failure(self, reason: str):
        ROUTING_FAILURES_TOTAL.labels(reason=reason).inc()

    def observe_cache_hit(self):
        ROUTING_CACHE_HITS.inc()

    def observe_cache_miss(self):
        ROUTING_CACHE_MISSES.inc()
