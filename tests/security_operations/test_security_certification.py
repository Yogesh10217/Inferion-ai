"""
Tests for Security Certification Engine (Phase 5.69).
"""

import pytest
from app.security_operations.security_posture import SecurityPostureEvaluator
from app.security_operations.security_policy_engine import SecurityPolicyEngine
from app.security_operations.compliance_governance import ComplianceGovernanceEngine
from app.security_operations.security_risk_engine import SecurityRiskEngine
from app.security_operations.audit_integrity import AuditIntegrityEngine
from app.security_operations.audit_log import SecurityAuditLogger
from app.security_operations.security_certification import SecurityCertificationEngine, SecurityCertificationResult


def test_security_certification_non_prod():
    posture_res = SecurityPostureEvaluator().evaluate(is_production=False)
    policy_res = SecurityPolicyEngine().evaluate_policy(posture_res, is_production=False)
    compliance_res = ComplianceGovernanceEngine().evaluate(posture_res, is_production=False)
    risk_res = SecurityRiskEngine().assess_risk(posture_res.score, [], [], is_production=False)
    audit_integrity = AuditIntegrityEngine(SecurityAuditLogger()).validate_audit_chain()

    cert_engine = SecurityCertificationEngine()
    result = cert_engine.certify(
        posture_res, policy_res, compliance_res, risk_res, audit_integrity, is_production=False
    )

    assert isinstance(result, SecurityCertificationResult)
    assert result.decision in [
        "SECURITY_CERTIFIED", "SECURITY_BLOCKED", "SECURITY_MANUAL_REVIEW_REQUIRED", "SECURITY_NOT_EXECUTED"
    ]
    assert result.fingerprint.startswith("sha256:")
