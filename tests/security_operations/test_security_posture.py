"""
Tests for Security Posture Evaluator (Phase 5.69).
"""

import pytest
from app.security_operations.security_posture import SecurityPostureEvaluator, SecurityPostureResult


def test_security_posture_evaluation_default():
    evaluator = SecurityPostureEvaluator()
    result = evaluator.evaluate(is_production=False)
    assert isinstance(result, SecurityPostureResult)
    assert 0.0 <= result.score <= 100.0
    assert result.status in ["SECURE", "WARNING", "AT_RISK", "CRITICAL", "BLOCKED"]
    assert result.fingerprint.startswith("sha256:")


def test_security_posture_evaluation_production_mode():
    evaluator = SecurityPostureEvaluator()
    result = evaluator.evaluate(is_production=True)
    assert isinstance(result, SecurityPostureResult)
    assert result.is_production is True
