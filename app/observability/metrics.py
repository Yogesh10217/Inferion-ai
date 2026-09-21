"""Prometheus Metrics definitions for Phase 5.8 Observability Platform."""

from __future__ import annotations

import logging
from typing import Optional

from prometheus_client import REGISTRY, CollectorRegistry, Counter, Gauge, Histogram

logger = logging.getLogger(__name__)


class ObservabilityMetrics:
    """Defines and manages Phase 5.8 Prometheus Observability metrics."""

    def __init__(self, registry: Optional[CollectorRegistry] = None) -> None:
        self.registry = registry or REGISTRY

        # Helper to safely register metrics avoiding duplication errors
        def get_or_create(metric_cls, name, documentation, labelnames=(), **kwargs):
            try:
                return metric_cls(name, documentation, labelnames=labelnames, registry=self.registry, **kwargs)
            except ValueError:
                # Metric already registered in this registry; retrieve existing
                if hasattr(self.registry, "_names_to_collectors"):
                    collector = self.registry._names_to_collectors.get(name)
                    if collector:
                        return collector
                # Fallback return standard definition
                return metric_cls(name, documentation, labelnames=labelnames, registry=None, **kwargs)

        self.ai_requests_total = get_or_create(
            Counter, "ai_requests_total", "Total AI requests received", ["provider", "model", "tenant_id"]
        )
        self.ai_request_duration_seconds = get_or_create(
            Histogram,
            "ai_request_duration_seconds",
            "Duration of AI requests in seconds",
            ["provider", "model"],
            buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, float("inf")),
        )
        self.ai_execution_total = get_or_create(
            Counter, "ai_execution_total", "Total AI component executions", ["component"]
        )
        self.ai_execution_failures_total = get_or_create(
            Counter, "ai_execution_failures_total", "Total AI component failures", ["component", "failure_category"]
        )
        self.ai_execution_duration_seconds = get_or_create(
            Histogram,
            "ai_execution_duration_seconds",
            "Duration of AI component executions",
            ["component"],
            buckets=(0.05, 0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, float("inf")),
        )
        self.ai_tokens_total = get_or_create(
            Counter,
            "ai_tokens_total",
            "Total AI tokens processed",
            ["type", "model"],  # type: input or output
        )
        self.ai_cost_total = get_or_create(
            Counter, "ai_cost_total", "Total AI financial cost accumulated in USD", ["tenant_id", "model"]
        )
        self.ai_active_executions = get_or_create(
            Gauge, "ai_active_executions", "Currently active AI executions", ["component"]
        )
        self.ai_agent_success_rate = get_or_create(
            Gauge, "ai_agent_success_rate", "Agent success rate metric (0.0 to 1.0)", ["agent_id"]
        )
        self.ai_workflow_success_rate = get_or_create(
            Gauge, "ai_workflow_success_rate", "Workflow success rate metric (0.0 to 1.0)", ["workflow_id"]
        )
        self.ai_tool_success_rate = get_or_create(
            Gauge, "ai_tool_success_rate", "Tool success rate metric (0.0 to 1.0)", ["tool_name"]
        )
        self.ai_anomalies_total = get_or_create(
            Counter, "ai_anomalies_total", "Total statistical anomalies detected", ["anomaly_type", "component"]
        )
        self.ai_alerts_total = get_or_create(
            Counter, "ai_alerts_total", "Total alerts triggered", ["level", "condition_type"]
        )
        self.ai_slo_violations_total = get_or_create(
            Counter, "ai_slo_violations_total", "Total SLO violations detected", ["slo_id", "component"]
        )
        self.ai_replays_total = get_or_create(
            Counter, "ai_replays_total", "Total execution replays initiated", ["component"]
        )
        self.ai_replay_failures_total = get_or_create(
            Counter, "ai_replay_failures_total", "Total execution replay failures", ["component"]
        )


_global_metrics: Optional[ObservabilityMetrics] = None


def get_observability_metrics(registry: Optional[CollectorRegistry] = None) -> ObservabilityMetrics:
    global _global_metrics
    if _global_metrics is None:
        _global_metrics = ObservabilityMetrics(registry)
    return _global_metrics
