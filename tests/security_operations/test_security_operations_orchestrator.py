"""
Tests for Security Operations Orchestrator (Phase 5.69).
"""

import pytest
from app.security_operations.security_operations_orchestrator import (
    SecurityOperationsOrchestrator,
    SecurityOperationsResult,
)


def test_orchestrator_full_assessment_non_prod():
    orchestrator = SecurityOperationsOrchestrator()
    result = orchestrator.run_security_assessment(
        target_name="Enterprise-AI-Platform-Test",
        is_production=False,
    )
    assert isinstance(result, SecurityOperationsResult)
    assert result.fingerprint.startswith("sha256:")
    assert result.posture_score >= 0.0
    assert result.compliance_score >= 0.0
    assert result.audit_integrity_passed is True


def test_orchestrator_full_assessment_prod():
    orchestrator = SecurityOperationsOrchestrator()
    result = orchestrator.run_security_assessment(
        target_name="Enterprise-AI-Platform-Prod",
        is_production=True,
    )
    assert isinstance(result, SecurityOperationsResult)
    assert result.is_production is True
    assert len(result.unexecuted_claims) > 0
    assert "PRODUCTION_PENETRATION_TEST_EXECUTED" in result.unexecuted_claims
