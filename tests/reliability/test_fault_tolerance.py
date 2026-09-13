"""
Tests for Fault Tolerance Module.
"""

from app.reliability.fault_tolerance import (
    FaultClassification,
    FaultScenario,
    FaultToleranceEngine,
    FaultType,
)


def test_fault_tolerance_simulated():
    engine = FaultToleranceEngine()
    scenario = FaultScenario(
        scenario_id="f01",
        fault_type=FaultType.DATABASE_FAILURE,
        description="Database outage test",
        is_simulation=True,
    )
    res = engine.evaluate_fault_scenario(scenario)
    assert res.system_recovered is True
    assert res.live_injection_blocked is True


def test_live_destructive_fault_injection_blocked():
    engine = FaultToleranceEngine()
    scenario = FaultScenario(
        scenario_id="f02",
        fault_type=FaultType.NETWORK_FAILURE,
        description="Live network partition test",
        is_simulation=False,
    )
    res = engine.evaluate_fault_scenario(scenario, live_injection_allowed=False)
    assert res.classification == FaultClassification.FAILED
    assert res.live_injection_blocked is True
