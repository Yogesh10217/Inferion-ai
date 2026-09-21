"""
Tests for Prometheus Metrics Subsystem
"""

from app.tools.tool_metrics import (
    tool_active_executions,
    tool_calls_total,
    tool_cost_total,
    tool_duration_seconds,
    tool_failures_total,
)


def test_prometheus_metrics_declarations():
    assert tool_calls_total._name == "tool_calls"
    assert tool_failures_total._name == "tool_failures"
    assert tool_duration_seconds._name == "tool_duration_seconds"
    assert tool_cost_total._name == "tool_cost"
    assert tool_active_executions._name == "tool_active_executions"


def test_prometheus_metrics_increment():
    tool_calls_total.labels(tool_name="metric_tool", status="success", tenant_id="tenant_1").inc()
    tool_cost_total.labels(tool_name="metric_tool", tenant_id="tenant_1").inc(0.01)
    tool_duration_seconds.labels(tool_name="metric_tool", tenant_id="tenant_1").observe(0.25)
