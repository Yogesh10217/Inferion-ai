"""
Tests for Security Risk Engine (Phase 5.69).
"""

import pytest
from app.security_operations.security_risk_engine import SecurityRiskEngine, RiskAssessment


def test_security_risk_assessment():
    engine = SecurityRiskEngine()
    assessment = engine.assess_risk(
        posture_score=95.0,
        vulnerabilities=[],
        active_exceptions=[],
        is_production=False,
    )
    assert isinstance(assessment, RiskAssessment)
    assert assessment.overall_risk_score >= 0.0
    assert assessment.overall_risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    assert assessment.fingerprint.startswith("sha256:")
