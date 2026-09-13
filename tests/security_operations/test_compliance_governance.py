"""
Tests for Compliance Governance Engine (Phase 5.69).
"""

import pytest
from app.security_operations.security_posture import SecurityPostureEvaluator
from app.security_operations.compliance_governance import ComplianceGovernanceEngine, ComplianceResult


def test_compliance_governance_evaluation():
    posture_eval = SecurityPostureEvaluator()
    posture_res = posture_eval.evaluate(is_production=False)
    engine = ComplianceGovernanceEngine()
    result = engine.evaluate(posture_res, is_production=False)
    assert isinstance(result, ComplianceResult)
    assert 0.0 <= result.overall_compliance_score <= 100.0
    assert len(result.framework_results) >= 4
    assert result.fingerprint.startswith("sha256:")
