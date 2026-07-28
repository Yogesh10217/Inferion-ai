import time
from typing import Any
from app.services.metrics_service import MetricsService
from app.observability.prometheus_registry import PrometheusRegistry


class MetricsMapper:
    """Translates engine metrics from MetricsService to Prometheus format."""

    def __init__(self, registry: PrometheusRegistry, metrics_service: MetricsService, version: str = "unknown"):
        self.registry = registry
        self.metrics = metrics_service
        self.start_time = time.time()
        self.version = version

        # Store last observed counts to calculate deltas for Prometheus Counters
        self._last_api_requests = 0
        self._last_api_errors = 0
        self._last_scheduler_processed = 0
        self._last_active_batches = 0
        self._last_tokens_consumed = 0
        self._last_quota_violations = 0
        self._last_redis_fallbacks = 0
        self._last_batches_dispatched = 0
        self._last_requests_batched = 0
        self._last_single_fallbacks = 0
        
        # Billing state tracking
        self._last_budget_violations = 0
        self._last_budget_warnings = 0
        self._last_invoice_count = 0
        self._last_provider_costs: dict[str, float] = {}
        
        self._last_cache_writes = 0
        self._last_cache_evictions = 0
        self._last_cache_hits = 0
        self._last_cache_misses = 0

        self._last_provider_requests = {}
        self._last_provider_failures = {}

        # Event & Webhook tracking
        self._last_webhook_deliveries = 0
        self._last_webhook_failures = 0
        self._last_webhook_retries = 0
        self._last_events_by_type: dict[str, int] = {}
        self._last_provider_failovers = {}

        # Limit & Quota Tracking
        self._last_rate_limit_requests = 0
        self._last_rate_limit_rejections = 0
        self._last_quota_violations = 0
        self._last_tokens_consumed = 0
        self._last_redis_fallbacks = 0

    def synchronize(self) -> None:
        """Fetch current metrics from MetricsService and push to PrometheusRegistry."""
        summary = self.metrics.get_metrics_summary()

        # --- Operational Metrics ---
        self.registry.uptime_seconds.set(time.time() - self.start_time)
        self.registry.app_info.labels(version=self.version).set(1)
        self.registry.active_requests.set(summary.get("queue_depth", 0) + summary.get("active_batches", 0))

        # --- API Metrics ---
        current_api_req = summary.get("request_count", 0)
        self.registry.api_requests_total.inc(current_api_req - self._last_api_requests)
        self._last_api_requests = current_api_req

        current_api_err = summary.get("error_count", 0)
        self.registry.api_errors_total.inc(current_api_err - self._last_api_errors)
        self._last_api_errors = current_api_err

        # --- Scheduler Metrics ---
        self.registry.scheduler_queue_depth.set(summary.get("queue_depth", 0))
        
        current_sched = summary.get("scheduler_throughput", 0)
        self.registry.scheduler_processed_total.inc(current_sched - self._last_scheduler_processed)
        self._last_scheduler_processed = current_sched

        # --- Batching Metrics ---
        self.registry.batching_active_batches.set(summary.get("active_batches", 0))
        self.registry.batching_largest_batch.set(summary.get("largest_observed_batch", 0))
        
        # total_batches_dispatched and batched counts
        # Because we need raw counts directly for counter calculation
        current_batches_dispatched = getattr(self.metrics, "_total_batches_dispatched", 0)
        self.registry.batching_batches_dispatched_total.inc(current_batches_dispatched - self._last_batches_dispatched)
        self._last_batches_dispatched = current_batches_dispatched

        current_requests_batched = getattr(self.metrics, "_total_requests_batched", 0)
        self.registry.batching_requests_batched_total.inc(current_requests_batched - self._last_requests_batched)
        self._last_requests_batched = current_requests_batched

        current_fallbacks = summary.get("single_request_fallbacks", 0)
        self.registry.batching_single_fallbacks_total.inc(current_fallbacks - self._last_single_fallbacks)
        self._last_single_fallbacks = current_fallbacks

        # --- Cache Metrics ---
        current_cache_writes = summary.get("cache_writes", 0)
        self.registry.cache_writes_total.inc(current_cache_writes - self._last_cache_writes)
        self._last_cache_writes = current_cache_writes

        current_cache_evictions = summary.get("cache_evictions", 0)
        self.registry.cache_evictions_total.inc(current_cache_evictions - self._last_cache_evictions)
        self._last_cache_evictions = current_cache_evictions

        current_hits = summary.get("cache_hits", 0)
        self.registry.cache_lookups_total.labels(result="hit").inc(current_hits - self._last_cache_hits)
        self._last_cache_hits = current_hits

        current_misses = summary.get("cache_misses", 0)
        self.registry.cache_lookups_total.labels(result="miss").inc(current_misses - self._last_cache_misses)
        self._last_cache_misses = current_misses

        # --- Load Balancer & Provider Metrics ---
        requests_per_instance = summary.get("requests_per_instance", {})
        provider_failures = summary.get("provider_failures", {})
        provider_failovers = summary.get("provider_failovers", {})

        # Active instances could be calculated based on health, but we don't have direct access to health state here.
        # We can just record requests and failures.

        for instance_id, count in requests_per_instance.items():
            parts = instance_id.split("::")
            prov_id = parts[0] if len(parts) > 1 else "unknown"
            inst_id = parts[1] if len(parts) > 1 else instance_id
            
            last_count = self._last_provider_requests.get(instance_id, 0)
            self.registry.provider_requests_total.labels(provider_id=prov_id, instance_id=inst_id).inc(count - last_count)
            self._last_provider_requests[instance_id] = count

        for key, count in provider_failures.items():
            parts = key.split("::")
            prov_id = parts[0] if len(parts) > 1 else "unknown"
            inst_id = parts[1] if len(parts) > 1 else key
            
            last_count = self._last_provider_failures.get(key, 0)
            self.registry.provider_failures_total.labels(provider_id=prov_id, instance_id=inst_id).inc(count - last_count)
            self._last_provider_failures[key] = count

        for prov_id, count in provider_failovers.items():
            last_count = self._last_provider_failovers.get(prov_id, 0)
            self.registry.provider_failovers_total.labels(provider_id=prov_id).inc(count - last_count)
            self._last_provider_failovers[prov_id] = count

        # --- Process Histogram Event Buffers ---
        events = self.metrics.drain_histograms()

        for lat in events.get("request_latencies", []):
            self.registry.api_request_duration_seconds.observe(lat / 1000.0)
            
        for lat in events.get("scheduler_wait_times", []):
            self.registry.scheduler_wait_duration_seconds.observe(lat / 1000.0)
            
        for lat in events.get("batch_dispatch_delays", []):
            self.registry.batching_dispatch_delay_seconds.observe(lat / 1000.0)
            
        for lat in events.get("cache_lookup_latencies", []):
            self.registry.cache_lookup_latency_seconds.observe(lat / 1000.0)
            
        for lat in events.get("cache_write_latencies", []):
            self.registry.cache_write_latency_seconds.observe(lat / 1000.0)

        for prov_id, inst_id, lat in events.get("provider_latencies", []):
            self.registry.provider_latency_seconds.labels(provider_id=prov_id, instance_id=inst_id).observe(lat / 1000.0)

        # --- Rate Limiting & Quotas ---
        limits_summary = self.metrics.get_limits_summary()
        
        current_rl_reqs = limits_summary.get("rate_limit_requests", 0)
        self.registry.rate_limit_requests_total.inc(current_rl_reqs - self._last_rate_limit_requests)
        self._last_rate_limit_requests = current_rl_reqs

        current_rl_rejs = limits_summary.get("rate_limit_rejections", 0)
        self.registry.rate_limit_rejections_total.inc(current_rl_rejs - self._last_rate_limit_rejections)
        self._last_rate_limit_rejections = current_rl_rejs

        current_quota_viols = limits_summary.get("quota_violations", 0)
        self.registry.quota_violations_total.inc(current_quota_viols - self._last_quota_violations)
        self._last_quota_violations = current_quota_viols

        current_tokens = limits_summary.get("tokens_consumed", 0)
        self.registry.tokens_consumed_total.inc(current_tokens - self._last_tokens_consumed)
        self._last_tokens_consumed = current_tokens

        if limits_summary.get("redis_fallback_events", 0) > self._last_redis_fallbacks:
            self.registry.redis_fallbacks_total.inc(limits_summary.get("redis_fallback_events", 0) - self._last_redis_fallbacks)
            self._last_redis_fallbacks = limits_summary.get("redis_fallback_events", 0)

        # Sync Billing Metrics
        billing_summary = self.metrics.get_billing_summary()
        
        if billing_summary["budget_violations"] > self._last_budget_violations:
            self.registry.budget_exceeded_total.inc(billing_summary["budget_violations"] - self._last_budget_violations)
            self._last_budget_violations = billing_summary["budget_violations"]

        if billing_summary["budget_warnings"] > self._last_budget_warnings:
            self.registry.budget_warnings_total.inc(billing_summary["budget_warnings"] - self._last_budget_warnings)
            self._last_budget_warnings = billing_summary["budget_warnings"]
            
        if billing_summary["invoice_generation_count"] > self._last_invoice_count:
            self.registry.invoice_generation_total.inc(billing_summary["invoice_generation_count"] - self._last_invoice_count)
            self._last_invoice_count = billing_summary["invoice_generation_count"]
            
        self.registry.monthly_recurring_revenue.set(billing_summary["mrr"])
        
        for plan_id, count in billing_summary["active_subscriptions"].items():
            self.registry.subscription_plan_total.labels(plan_id=plan_id).set(count)
            
        for provider, cost in billing_summary["provider_costs"].items():
            last_cost = self._last_provider_costs.get(provider, 0.0)
            if cost > last_cost:
                self.registry.billing_cost_total.labels(provider_id=provider).inc(cost - last_cost)
                self._last_provider_costs[provider] = cost

        # Drain and sync billing histograms
        billing_histograms = self.metrics.drain_billing_histograms()
        for duration in billing_histograms["invoice_durations"]:
            self.registry.invoice_generation_seconds.observe(duration / 1000.0)

        self.registry.concurrent_requests.set(limits_summary.get("concurrent_requests", 0))

        # --- Event & Webhook Metrics ---
        if hasattr(self.metrics, "get_event_summary"):
            event_summary = self.metrics.get_event_summary()
            
            for ev_type, count in event_summary.get("events_by_type", {}).items():
                last_count = self._last_events_by_type.get(ev_type, 0)
                if count > last_count:
                    self.registry.events_total.labels(event_type=ev_type).inc(count - last_count)
                    self._last_events_by_type[ev_type] = count

            deliv_count = event_summary.get("webhook_deliveries_total", 0)
            if deliv_count > self._last_webhook_deliveries:
                self.registry.webhook_deliveries_total.inc(deliv_count - self._last_webhook_deliveries)
                self._last_webhook_deliveries = deliv_count

            fail_count = event_summary.get("webhook_failure_count", 0)
            if fail_count > self._last_webhook_failures:
                self.registry.webhook_failures_total.inc(fail_count - self._last_webhook_failures)
                self._last_webhook_failures = fail_count

            retry_count = event_summary.get("webhook_retries_total", 0)
            if retry_count > self._last_webhook_retries:
                self.registry.webhook_retries_total.inc(retry_count - self._last_webhook_retries)
                self._last_webhook_retries = retry_count

            self.registry.dead_letter_total.set(event_summary.get("dead_letter_queue_size", 0))

        # --- Admin System Stats ---
        # Fetching stats from SystemAdminService would ideally happen here, but since MetricsMapper
        # is synchronous and decoupled from DB session, we will expose an endpoint to trigger stat 
        # collection, or rely on an async background task to update the metrics periodically.
        # Alternatively, the admin endpoints themselves will increment the counters when actions happen.
