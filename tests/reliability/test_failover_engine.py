"""
Tests for Failover Engine Module.
"""

from app.reliability.failover_engine import FailoverEngine, FailoverPlan, FailoverState, FailoverTrigger


def test_failover_recommendation():
    engine = FailoverEngine()
    plan = FailoverPlan("plan-db", FailoverTrigger.DATABASE_FAILURE, "primary", "secondary")
    res = engine.evaluate_failover(plan, trigger_active=True)
    assert res.state == FailoverState.RECOMMENDED
    assert res.auto_execution_blocked is True
    assert res.production_failover_executed is False
