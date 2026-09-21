"""
Tests for Recovery Validation Engine Module.
"""

from app.reliability.recovery_validation import RecoveryValidationEngine
from app.reliability.reliability_models import ReliabilityStatus


def test_recovery_validation_probes_and_invariants():
    engine = RecoveryValidationEngine()
    res = engine.validate_recovery(live_probe=True, ready_probe=True, health_probe=True)
    assert res.healthy is True
    assert res.status == ReliabilityStatus.HEALTHY
    assert res.container_invariant_passed is True
    assert res.managers_validation_passed is True
