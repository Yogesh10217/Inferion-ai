"""Tests for Observability Prometheus Metrics registry."""

import pytest
from prometheus_client import CollectorRegistry
from app.observability.metrics import ObservabilityMetrics


def test_observability_metrics_initialization():
    registry = CollectorRegistry()
    metrics = ObservabilityMetrics(registry)

    metrics.ai_requests_total.labels(provider="openai", model="gpt-4o", tenant_id="t1").inc()
    metrics.ai_execution_total.labels(component="agent").inc()

    output = registry.get_sample_value("ai_execution_total", {"component": "agent"})
    assert output == 1.0
