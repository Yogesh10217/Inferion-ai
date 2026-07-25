from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram


class PrometheusRegistry:
    """Maintains the Prometheus CollectorRegistry and all metric definitions."""

    def __init__(self, namespace: str = "llm_engine", subsystem: str = "inference"):
        self.registry = CollectorRegistry()
        self.namespace = namespace
        self.subsystem = subsystem

        prefix = f"{namespace}_{subsystem}_"

        # --- Operational Metrics ---
        self.uptime_seconds = Gauge(
            "uptime_seconds",
            "Application uptime in seconds",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.app_info = Gauge(
            "app_info",
            "Application version and build information",
            ["version"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.active_requests = Gauge(
            "active_requests",
            "Currently active inference requests",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )

        # --- API Metrics ---
        self.api_requests_total = Counter(
            "api_requests_total",
            "Total number of API requests",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.api_errors_total = Counter(
            "api_errors_total",
            "Total number of failed API requests",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        # Latency buckets (seconds): 100ms, 500ms, 1s, 2.5s, 5s, 10s, 30s, 60s, 120s, 300s
        self.api_request_duration_seconds = Histogram(
            "api_request_duration_seconds",
            "Histogram of API request durations",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
            buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0, float("inf")),
        )

        # --- Scheduler Metrics ---
        self.scheduler_queue_depth = Gauge(
            "scheduler_queue_depth",
            "Current depth of the scheduler queue",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.scheduler_processed_total = Counter(
            "scheduler_processed_total",
            "Total number of requests processed by the scheduler",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        # Wait latency buckets (seconds): 1ms, 5ms, 10ms, 50ms, 100ms, 500ms, 1s, 5s
        self.scheduler_wait_duration_seconds = Histogram(
            "scheduler_wait_duration_seconds",
            "Histogram of time spent waiting in the scheduler queue",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, float("inf")),
        )

        # --- Batching Metrics ---
        self.batching_active_batches = Gauge(
            "batching_active_batches",
            "Currently active batches",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.batching_requests_batched_total = Counter(
            "batching_requests_batched_total",
            "Total requests successfully batched",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.batching_batches_dispatched_total = Counter(
            "batching_batches_dispatched_total",
            "Total batches dispatched",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.batching_largest_batch = Gauge(
            "batching_largest_batch",
            "Largest observed batch size",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.batching_single_fallbacks_total = Counter(
            "batching_single_fallbacks_total",
            "Total single request fallbacks (unbatched)",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        # Dispatch delay buckets (seconds)
        self.batching_dispatch_delay_seconds = Histogram(
            "batching_dispatch_delay_seconds",
            "Histogram of batch dispatch delays",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, float("inf")),
        )

        # --- Load Balancer & Provider Metrics ---
        self.provider_requests_total = Counter(
            "provider_requests_total",
            "Total requests sent to providers",
            ["provider_id", "instance_id"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.provider_failures_total = Counter(
            "provider_failures_total",
            "Total provider execution failures",
            ["provider_id", "instance_id"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.provider_failovers_total = Counter(
            "provider_failovers_total",
            "Total number of provider failover events",
            ["provider_id"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.provider_active_instances = Gauge(
            "provider_active_instances",
            "Number of active (healthy) provider instances",
            ["provider_id"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.provider_latency_seconds = Histogram(
            "provider_latency_seconds",
            "Histogram of provider execution latencies",
            ["provider_id", "instance_id"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
            buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, float("inf")),
        )

        # --- Caching Metrics ---
        self.cache_lookups_total = Counter(
            "cache_lookups_total",
            "Total cache lookups",
            ["result"],  # result="hit" or "miss"
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.cache_writes_total = Counter(
            "cache_writes_total",
            "Total cache writes",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.cache_evictions_total = Counter(
            "cache_evictions_total",
            "Total cache evictions",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.cache_lookup_latency_seconds = Histogram(
            "cache_lookup_latency_seconds",
            "Histogram of cache lookup latencies",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, float("inf")),
        )
        self.cache_write_latency_seconds = Histogram(
            "cache_write_latency_seconds",
            "Histogram of cache write latencies",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
            buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, float("inf")),
        )
