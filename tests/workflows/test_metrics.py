"""
Tests for Prometheus & OpenTelemetry Workflow Observability Metrics
"""

from app.observability.prometheus_registry import PrometheusRegistry


def test_prometheus_workflow_metrics_registration():
    registry = PrometheusRegistry(namespace="test_llm", subsystem="test_wf")
    assert hasattr(registry, "workflow_runs_total")
    assert hasattr(registry, "workflow_failures_total")
    assert hasattr(registry, "workflow_pauses_total")
    assert hasattr(registry, "workflow_resumes_total")
    assert hasattr(registry, "workflow_approval_requests_total")
    assert hasattr(registry, "workflow_node_executions_total")
    assert hasattr(registry, "workflow_duration_seconds")
