"""
Tests for Reliability Certification Module.
"""

from app.reliability.reliability_certification import (
    ReliabilityCertificationDecision,
    ReliabilityCertificationEngine,
)


def test_reliability_certification_decision():
    engine = ReliabilityCertificationEngine()
    res = engine.evaluate_certification()
    assert res.certified is True
    assert res.decision == ReliabilityCertificationDecision.RELIABILITY_CERTIFIED
    assert res.live_production_recovery_validated is False
