"""
Tests for Security Dashboard (Phase 5.69).
"""

import pytest
from app.security_operations.security_posture import SecurityPostureEvaluator
from app.security_operations.security_policy_engine import SecurityPolicyEngine
from app.security_operations.compliance_governance import ComplianceGovernanceEngine
from app.security_operations.security_risk_engine import SecurityRiskEngine
from app.security_operations.security_certification import SecurityCertificationEngine
from app.security_operations.audit_integrity import AuditIntegrityEngine
from app.security_operations.audit_log import SecurityAuditLogger
from app.security_operations.security_metrics import SecurityMetricsCalculator
from app.security_operations.security_dashboard import SecurityDashboard, SecurityDashboardSnapshot


def test_security_dashboard_snapshot_generation():
    posture_res = SecurityPostureEvaluator().evaluate(is_production=False)
    policy_res = SecurityPolicyEngine().evaluate_policy(posture_res, is_production=False)
    compliance_res = ComplianceGovernanceEngine().evaluate(posture_res, is_production=False)
    risk_res = SecurityRiskEngine().assess_risk(posture_res.score, [], [], is_production=False)
    audit_integrity = AuditIntegrityEngine(SecurityAuditLogger()).validate_audit_chain()
    cert_res = SecurityCertificationEngine().certify(
        posture_res, policy_res, compliance_res, risk_res, audit_integrity, is_production=False
    )
    metrics_res = SecurityMetricsCalculator().calculate_metrics(
        posture_res.score, posture_res.vulnerability_assessment, 0, compliance_res.overall_compliance_score, False
    )

    dashboard = SecurityDashboard()
    snapshot = dashboard.generate_snapshot(
        posture_result=posture_res,
        metrics_result=metrics_res,
        risk_assessment=risk_res,
        compliance_result=compliance_res,
        audit_integrity=audit_integrity,
        certification_result=cert_res,
        is_production=False,
    )

    assert isinstance(snapshot, SecurityDashboardSnapshot)
    assert snapshot.overall_posture_score == posture_res.score
    assert snapshot.certification_decision == cert_res.decision
    assert snapshot.fingerprint.startswith("sha256:")
