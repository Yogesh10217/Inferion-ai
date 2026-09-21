from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram


class PrometheusRegistry:
    """Maintains the Prometheus CollectorRegistry and all metric definitions."""

    def __init__(self, namespace: str = "llm_engine", subsystem: str = "inference"):
        self.registry = CollectorRegistry()
        self.namespace = namespace
        self.subsystem = subsystem


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

        # --- Rate Limiting & Quotas Metrics ---
        self.rate_limit_requests_total = Counter(
            "rate_limit_requests_total",
            "Total rate limit checks",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.rate_limit_rejections_total = Counter(
            "rate_limit_rejections_total",
            "Total rate limit rejections (429s)",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.quota_remaining = Gauge(
            "quota_remaining",
            "Remaining quota units for a given scope",
            ["scope_id", "quota_type"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.tokens_consumed_total = Counter(
            "tokens_consumed_total",
            "Total tokens consumed",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.concurrent_requests = Gauge(
            "concurrent_requests",
            "Currently active concurrent requests evaluated by rate limiter",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.quota_violations_total = Counter(
            "quota_violations_total",
            "Total quota violations",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.redis_fallbacks_total = Counter(
            "redis_fallbacks_total",
            "Total times rate limiter fell back to memory backend",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )

        # --- Billing & Subscription Metrics ---
        self.billing_cost_total = Counter(
            "billing_cost_total",
            "Total accumulated cost in currency",
            ["provider_id"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.budget_exceeded_total = Counter(
            "budget_exceeded_total",
            "Total number of hard budget violations",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.budget_warnings_total = Counter(
            "budget_warnings_total",
            "Total number of budget warning thresholds crossed",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.invoice_generation_total = Counter(
            "invoice_generation_total",
            "Total number of invoices generated",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.subscription_plan_total = Gauge(
            "subscription_plan_total",
            "Number of organizations on each subscription plan",
            ["plan_id"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.monthly_recurring_revenue = Gauge(
            "monthly_recurring_revenue",
            "Current MRR calculated from active subscriptions",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.invoice_generation_seconds = Histogram(
            "invoice_generation_seconds",
            "Histogram of invoice generation duration",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
            buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, float("inf")),
        )

        # --- Admin Metrics ---
        self.admin_users_total = Gauge(
            "admin_users_total",
            "Total number of active and disabled users",
            ["status"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.admin_orgs_total = Gauge(
            "admin_orgs_total",
            "Total number of active and suspended organizations",
            ["status"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.admin_reports_total = Gauge(
            "admin_reports_total",
            "Total number of generated reports",
            ["status"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.admin_audit_queries_total = Counter(
            "admin_audit_queries_total",
            "Total number of audit queries executed",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )

        # --- Event & Webhook Metrics ---
        self.events_total = Counter(
            "events_total",
            "Total number of events published",
            ["event_type"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.webhook_deliveries_total = Counter(
            "webhook_deliveries_total",
            "Total number of webhook delivery attempts",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.webhook_failures_total = Counter(
            "webhook_failures_total",
            "Total number of failed webhook delivery attempts",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.webhook_retries_total = Counter(
            "webhook_retries_total",
            "Total number of webhook delivery retries",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.dead_letter_total = Gauge(
            "dead_letter_total",
            "Current number of events in dead-letter queue",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )

        # --- Plugin Metrics ---
        self.plugins_total = Gauge(
            "plugins_total",
            "Total number of installed plugins",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.plugin_enabled_total = Gauge(
            "plugin_enabled_total",
            "Total number of enabled plugins",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.plugin_failures_total = Counter(
            "plugin_failures_total",
            "Total number of plugin execution failures",
            ["plugin_id"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.plugin_invocations_total = Counter(
            "plugin_invocations_total",
            "Total number of plugin invocations",
            ["plugin_id"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.plugin_timeouts_total = Counter(
            "plugin_timeouts_total",
            "Total number of plugin timeouts",
            ["plugin_id"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.plugin_permission_denials_total = Counter(
            "plugin_permission_denials_total",
            "Total number of plugin permission denials",
            ["plugin_id"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.plugin_execution_seconds = Histogram(
            "plugin_execution_seconds",
            "Histogram of plugin execution duration",
            ["plugin_id"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0, float("inf")),
        )
        self.plugin_load_seconds = Histogram(
            "plugin_load_seconds",
            "Histogram of plugin load times",
            ["plugin_id"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
            buckets=(0.1, 0.5, 1.0, 5.0, 10.0, float("inf")),
        )

        # --- Workflow Metrics ---
        self.workflow_runs_total = Counter(
            "workflow_runs_total",
            "Total number of workflow runs initiated",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.workflow_failures_total = Counter(
            "workflow_failures_total",
            "Total number of failed workflow runs",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.workflow_pauses_total = Counter(
            "workflow_pauses_total",
            "Total number of paused workflow runs",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.workflow_resumes_total = Counter(
            "workflow_resumes_total",
            "Total number of resumed workflow runs",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.workflow_approval_requests_total = Counter(
            "workflow_approval_requests_total",
            "Total number of human approval requests created",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.workflow_node_executions_total = Counter(
            "workflow_node_executions_total",
            "Total number of workflow node executions",
            ["node_type"],
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.workflow_duration_seconds = Histogram(
            "workflow_duration_seconds",
            "Histogram of workflow run execution duration",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
            buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0, float("inf")),
        )

        # --- Memory Metrics ---
        self.memory_reads_total = Counter(
            "memory_reads_total",
            "Total number of memory read operations",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.memory_writes_total = Counter(
            "memory_writes_total",
            "Total number of memory write operations",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.memory_searches_total = Counter(
            "memory_searches_total",
            "Total number of memory search queries",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.memory_compressions_total = Counter(
            "memory_compressions_total",
            "Total number of memory compression operations",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.memory_summaries_total = Counter(
            "memory_summaries_total",
            "Total number of memory summary operations",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.memory_expirations_total = Counter(
            "memory_expirations_total",
            "Total number of memory record expirations",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.memory_embeddings_total = Counter(
            "memory_embeddings_total",
            "Total number of memory embeddings generated",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.memory_vector_search_total = Counter(
            "memory_vector_search_total",
            "Total number of memory vector searches",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.memory_cache_hits_total = Counter(
            "memory_cache_hits_total",
            "Total number of memory cache hits",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.memory_cache_misses_total = Counter(
            "memory_cache_misses_total",
            "Total number of memory cache misses",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.memory_storage_bytes = Gauge(
            "memory_storage_bytes",
            "Total memory storage usage in bytes",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
        )
        self.memory_retrieval_latency_seconds = Histogram(
            "memory_retrieval_latency_seconds",
            "Histogram of memory retrieval latency",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
            buckets=(0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, float("inf")),
        )
        self.memory_compression_latency_seconds = Histogram(
            "memory_compression_latency_seconds",
            "Histogram of memory compression latency",
            registry=self.registry,
            namespace=namespace,
            subsystem=subsystem,
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0, float("inf")),
        )
