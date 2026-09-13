"""
Tests for Resilience Testing Module.
"""

from app.reliability.resilience_testing import (
    ResilienceTest,
    ResilienceTestingEngine,
    ResilienceTestMode,
)


def test_resilience_test_simulation():
    engine = ResilienceTestingEngine()
    test = ResilienceTest("rt01", "Simulation Test", "database", ResilienceTestMode.SIMULATION)
    res = engine.run_resilience_test(test)
    assert res.passed is True
    assert res.status == "PASSED"


def test_resilience_test_production_target_unconfigured():
    engine = ResilienceTestingEngine()
    test = ResilienceTest("rt02", "Production Test", "cluster", ResilienceTestMode.PRODUCTION)
    res = engine.run_resilience_test(test, target_configured=False)
    assert res.passed is False
    assert res.status == "BLOCKED"
