"""
Tests for Business Continuity Engine Module.
"""

from app.reliability.business_continuity import (
    BusinessContinuityEngine,
    BusinessContinuityPlan,
    ContinuityClassification,
)


def test_business_continuity_prioritization():
    engine = BusinessContinuityEngine()
    plan = BusinessContinuityPlan("bcp-test", "BCP Test Plan")
    res = engine.evaluate_continuity(plan, simulated_capability_percentage=95.0)
    assert res.classification == ContinuityClassification.CONTINUITY_READY
    assert res.minimum_capability_met is True
    assert res.production_bc_executed is False
