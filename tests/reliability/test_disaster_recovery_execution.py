"""
Tests for Disaster Recovery Execution Module.
"""

from app.reliability.disaster_recovery_execution import (
    DisasterRecoveryExecutionEngine,
    DisasterRecoveryPlan,
    RecoveryExecutionState,
)


def test_dr_plan_simulation():
    engine = DisasterRecoveryExecutionEngine()
    plan = DisasterRecoveryPlan("dr01", "DR Simulation Plan", "simulation")
    res = engine.evaluate_dr_plan(plan)
    assert res.execution_state == RecoveryExecutionState.RECOVERY_READY
    assert res.auto_execution_blocked is True
    assert res.is_simulation is True


def test_dr_plan_production_blocked():
    engine = DisasterRecoveryExecutionEngine()
    plan = DisasterRecoveryPlan("dr02", "DR Prod Plan", "production")
    res = engine.evaluate_dr_plan(plan, real_production_configured=False)
    assert res.execution_state == RecoveryExecutionState.MANUAL_EXECUTION_REQUIRED
    assert res.auto_execution_blocked is True
