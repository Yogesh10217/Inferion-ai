"""
Tests for Truthfulness Contract & Unexecuted Production Claims (Phase 5.69).
"""

import pytest
from app.security_operations.security_certification import (
    SecurityCertificationEngine,
    UNEXECUTED_PRODUCTION_CLAIMS,
)
from app.security_operations.security_operations_orchestrator import SecurityOperationsOrchestrator


def test_unexecuted_claims_list():
    assert "PRODUCTION_PENETRATION_TEST_EXECUTED" in UNEXECUTED_PRODUCTION_CLAIMS
    assert "PRODUCTION_VULNERABILITY_SCAN_EXECUTED" in UNEXECUTED_PRODUCTION_CLAIMS
    assert "PRODUCTION_SECRET_ROTATION_EXECUTED" in UNEXECUTED_PRODUCTION_CLAIMS
    assert "LIVE_PRODUCTION_SECURITY_VALIDATED" in UNEXECUTED_PRODUCTION_CLAIMS


def test_truthfulness_boundary_in_orchestrator():
    orchestrator = SecurityOperationsOrchestrator()
    prod_result = orchestrator.run_security_assessment(is_production=True)
    assert prod_result.is_production is True
    assert len(prod_result.unexecuted_claims) == len(UNEXECUTED_PRODUCTION_CLAIMS)
    assert prod_result.certification_decision == "SECURITY_NOT_EXECUTED"
    assert prod_result.is_certified is False
