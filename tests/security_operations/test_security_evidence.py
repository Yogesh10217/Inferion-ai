"""
Tests for Security Evidence Collector (Phase 5.69).
"""

from app.security_operations.audit_integrity import AuditIntegrityEngine
from app.security_operations.audit_log import SecurityAuditLogger
from app.security_operations.compliance_governance import ComplianceGovernanceEngine
from app.security_operations.security_certification import SecurityCertificationEngine
from app.security_operations.security_evidence import SecurityEvidence, SecurityEvidenceCollector
from app.security_operations.security_policy_engine import SecurityPolicyEngine
from app.security_operations.security_posture import SecurityPostureEvaluator
from app.security_operations.security_risk_engine import SecurityRiskEngine


def test_security_evidence_collection():
    posture_res = SecurityPostureEvaluator().evaluate(is_production=False)
    policy_res = SecurityPolicyEngine().evaluate_policy(posture_res, is_production=False)
    compliance_res = ComplianceGovernanceEngine().evaluate(posture_res, is_production=False)
    risk_res = SecurityRiskEngine().assess_risk(posture_res.score, [], [], is_production=False)

    audit_logger = SecurityAuditLogger()
    audit_integrity = AuditIntegrityEngine(audit_logger).validate_audit_chain()

    cert_res = SecurityCertificationEngine().certify(
        posture_res, policy_res, compliance_res, risk_res, audit_integrity, is_production=False
    )

    collector = SecurityEvidenceCollector()
    evidence = collector.collect_evidence(
        posture_res, policy_res, compliance_res, risk_res, cert_res, is_production=False
    )

    assert isinstance(evidence, SecurityEvidence)
    assert evidence.fingerprint.startswith("sha256:")
    assert evidence.evidence_id.startswith("EVID-")
