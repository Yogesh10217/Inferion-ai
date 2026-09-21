"""
Tests for Autonomy Prometheus Metrics
"""

from app.autonomy.execution_metrics import (
    autonomous_checkpoints_total,
    autonomous_runs_active,
    autonomous_runs_completed,
    autonomous_runs_total,
)


def test_autonomy_metrics_declarations():
    assert autonomous_runs_total._name == "autonomous_runs"
    assert autonomous_runs_active._name == "autonomous_runs_active"
    assert autonomous_runs_completed._name == "autonomous_runs_completed"


def test_autonomy_metrics_increment():
    autonomous_runs_total.labels(tenant_id="t1", execution_mode="goal_driven").inc()
    autonomous_checkpoints_total.labels(tenant_id="t1").inc()
