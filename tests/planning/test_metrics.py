"""
Tests for Planning Prometheus Metrics
"""

from app.planning.planning_metrics import (
    planning_confidence_score,
    plans_completed_total,
    plans_created_total,
    simulations_run_total,
)


def test_planning_metrics_declarations():
    assert plans_created_total._name == "plans_created"
    assert plans_completed_total._name == "plans_completed"
    assert simulations_run_total._name == "simulations_run"


def test_planning_metrics_increment():
    plans_created_total.labels(tenant_id="tenant_1").inc()
    simulations_run_total.labels(tenant_id="tenant_1").inc()
    planning_confidence_score.labels(plan_id="p1").set(0.95)
