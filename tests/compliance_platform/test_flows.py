"""Mandatory 12 E2E Verification Flows for Enterprise AI Compliance Platform (Phase 5.27)."""

import pytest

from app.compliance_platform.assessments import AssessmentResult
from app.compliance_platform.assurance import AssuranceConclusion
from app.compliance_platform.continuous_monitoring import ComplianceSignalType
from app.compliance_platform.controls import ControlCategory, ControlImplementation, ControlStatus, ControlType
from app.compliance_platform.evidence import EvidenceSource, EvidenceType
from app.compliance_platform.exceptions import (
    AttestationExpiredException,
    CrossTenantComplianceAccessException,
)
from app.compliance_platform.findings import FindingCategory, FindingSeverity
from app.compliance_platform.frameworks import FrameworkType
from app.compliance_platform.manager import CompliancePlatformManager
from app.compliance_platform.posture import PostureBand
from app.compliance_platform.remediation import RemediationAction, RemediationPriority, RemediationStatus


@pytest.fixture
def manager():
    return CompliancePlatformManager()


def test_flow1_full_compliance_assessment(manager):
    """Flow 1: Framework -> Requirement Applicability -> Control Mapping -> Evidence Collection -> Assessment -> Posture."""
    res = manager.run_full_compliance_flow(tenant_id="tenant_alpha", framework_type=FrameworkType.SOC_2)
    assert res["assessment"]["overall_result"] == AssessmentResult.PASS
    assert res["posture"]["overall_score"] >= 90.0
    assert res["assurance_report"]["conclusion"] == AssuranceConclusion.ASSURED


def test_flow2_missing_evidence(manager):
    """Flow 2: Missing Evidence prevents PASS and returns INSUFFICIENT_EVIDENCE."""
    fw = manager.framework_manager.adopt_framework("tenant_beta", FrameworkType.ISO_27001, "ISO 27001", "Desc")
    req = manager.requirement_manager.register_requirement("tenant_beta", fw.framework_id, "ISO-01", "Title", "Desc")
    impl = ControlImplementation(source_subsystem="Security", method_name="check")
    ctrl = manager.control_manager.register_control(
        tenant_id="tenant_beta",
        code="CTRL-ISO-01",
        name="Control",
        description="Desc",
        control_type=ControlType.PREVENTIVE,
        category=ControlCategory.SECURITY,
        implementation=impl,
        requirement_ids=[req.requirement_id],
    )
    manager.mapping_manager.map_requirement_to_control("tenant_beta", req.requirement_id, ctrl.control_id)

    # Run assessment without submitting evidence
    assessment = manager.assessment_manager.run_assessment("tenant_beta", fw.framework_id, subject_id="no_ev_subject")
    assert assessment.overall_result == AssessmentResult.INSUFFICIENT_EVIDENCE
    assert assessment.overall_result != AssessmentResult.PASS


def test_flow3_control_failure(manager):
    """Flow 3: Simulated control failure -> finding generation -> risk evaluation -> remediation plan -> posture degradation."""
    tenant = "tenant_gamma"
    fw = manager.framework_manager.adopt_framework(tenant, FrameworkType.EU_AI_ACT, "EU AI Act", "Desc")
    req = manager.requirement_manager.register_requirement(tenant, fw.framework_id, "EU-01", "Safety", "Desc")
    impl = ControlImplementation(source_subsystem="ModelManager", method_name="verify_safety")
    ctrl = manager.control_manager.register_control(
        tenant_id=tenant,
        code="CTRL-SAFETY-01",
        name="Safety Control",
        description="Desc",
        control_type=ControlType.PREVENTIVE,
        category=ControlCategory.MODEL,
        implementation=impl,
        requirement_ids=[req.requirement_id],
    )
    manager.control_manager.update_control_status(ctrl.control_id, tenant, ControlStatus.FAILED)

    # Finding & Remediation
    finding = manager.finding_manager.create_finding(
        tenant_id=tenant,
        title="Safety Control Failed",
        description="Control failed operational checks",
        severity=FindingSeverity.HIGH,
        category=FindingCategory.CONTROL_FAILURE,
        control_id=ctrl.control_id,
    )
    action = RemediationAction(
        target_subsystem="OrchestrationManager", action_type="RESTART_GUARDRAIL", description="Restart guardrails"
    )
    plan = manager.remediation_manager.create_remediation_plan(
        tenant, finding.finding_id, [action], priority=RemediationPriority.HIGH, risk_level="HIGH"
    )

    # Posture degradation
    posture = manager.posture_manager.calculate_posture(
        tenant, has_critical_finding=True, critical_finding_details=["Control Safety Failed"]
    )
    assert posture.overall_score < 50.0
    assert posture.posture_band == PostureBand.NON_COMPLIANT
    assert plan.status == RemediationStatus.REQUIRES_APPROVAL


def test_flow4_high_risk_remediation(manager):
    """Flow 4: High-Risk Remediation requires ApprovalEngine approval and delegates execution after approval."""
    tenant = "tenant_delta"
    finding = manager.finding_manager.create_finding(
        tenant, "Critical Breach", "Breach detected", severity=FindingSeverity.CRITICAL
    )
    action = RemediationAction(
        target_subsystem="PlatformOperationsManager", action_type="ISOLATE_POD", description="Isolate pod"
    )

    plan = manager.remediation_manager.create_remediation_plan(
        tenant, finding.finding_id, [action], priority=RemediationPriority.CRITICAL, risk_level="CRITICAL"
    )
    assert plan.status == RemediationStatus.REQUIRES_APPROVAL

    # Approve request via ApprovalEngine
    manager.governance_engine.approval_engine.approve(plan.approval_request_id, approver_id="security_lead")

    # Now delegate execution
    plan.status = RemediationStatus.APPROVED
    del_plan = manager.remediation_manager.delegate_execution(
        plan.plan_id, tenant, delegated_subsystem="PlatformOperationsManager"
    )
    assert del_plan.status == RemediationStatus.COMPLETED
    assert del_plan.delegated_subsystem == "PlatformOperationsManager"


def test_flow5_expired_attestation(manager):
    """Flow 5: Expired Attestation affects posture and raises exception on retrieval."""
    tenant = "tenant_epsilon"
    att = manager.attestation_manager.submit_attestation(tenant, "ctrl_01", "Operating correctly", valid_days=1)
    manager.attestation_manager.expire_attestation_explicitly(att.attestation_id, tenant)

    # Continuous monitoring signal
    sig = manager.monitoring_manager.emit_signal(
        tenant, ComplianceSignalType.ATTESTATION_EXPIRED, "AttestationManager", att.attestation_id
    )
    assert sig.signal_type == ComplianceSignalType.ATTESTATION_EXPIRED

    with pytest.raises(AttestationExpiredException):
        manager.attestation_manager.get_attestation(att.attestation_id, tenant)


def test_flow6_compliance_exception_lifecycle(manager):
    """Flow 6: Exception Request -> Approval -> Active -> Expiration (expired exception stops suppressing findings)."""
    tenant = "tenant_zeta"
    exc = manager.exception_manager.request_exception(
        tenant, "req_01", "Business exception rationale", duration_days=30
    )
    assert manager.exception_manager.is_requirement_excepted(tenant, "req_01") is True

    # Expire exception explicitly
    manager.exception_manager.expire_exception_explicitly(exc.exception_id, tenant)
    assert manager.exception_manager.is_requirement_excepted(tenant, "req_01") is False


def test_flow7_architecture_drift_compliance(manager):
    """Flow 7: Architecture Drift Event -> Compliance Signal -> Control Reassessment -> Finding."""
    tenant = "tenant_eta"
    sig = manager.monitoring_manager.emit_signal(
        tenant,
        signal_type=ComplianceSignalType.ARCHITECTURE_DRIFT,
        source_system="ArchitecturePlatformManager",
        subject_id="topo_snapshot_01",
        severity="HIGH",
        details={"unauthorized_node": "unapproved_agent"},
    )
    assert sig.signal_type == ComplianceSignalType.ARCHITECTURE_DRIFT

    finding = manager.finding_manager.create_finding(
        tenant_id=tenant,
        title="Architecture Drift Compliance Violation",
        description=f"Drift detected in topology: {sig.subject_id}",
        severity=FindingSeverity.HIGH,
        category=FindingCategory.UNAUTHORIZED_CHANGE,
    )
    assert finding.category == FindingCategory.UNAUTHORIZED_CHANGE


def test_flow8_data_governance_violation(manager):
    """Flow 8: Governed Data Access / Privacy Violation -> Evidence Reference -> Finding -> Audit Trail."""
    tenant = "tenant_theta"
    ev = manager.evidence_manager.collect_evidence(
        tenant_id=tenant,
        subject_type="DATA_ASSET",
        subject_id="asset_pii_01",
        evidence_type=EvidenceType.DATA_GOVERNANCE_DECISION,
        source_system=EvidenceSource.DATA_GOVERNANCE_MANAGER,
        source_reference="data_gov_ref_1001",
        metadata={"decision": "REJECTED_UNAUTHORIZED_PURPOSE"},
    )

    finding = manager.finding_manager.create_finding(
        tenant_id=tenant,
        title="Data Governance Violation",
        description="Unauthorized purpose data retrieval attempt",
        severity=FindingSeverity.HIGH,
        category=FindingCategory.GOVERNANCE_VIOLATION,
        evidence_ids=[ev.evidence_id],
    )
    assert len(finding.evidence_ids) == 1


def test_flow9_cross_tenant_isolation(manager):
    """Flow 9: Cross-tenant access attempt raises CrossTenantComplianceAccessException without metadata leakage."""
    fw = manager.framework_manager.adopt_framework("tenant_tenant1", FrameworkType.SOC_2, "SOC2", "Desc")

    with pytest.raises(CrossTenantComplianceAccessException) as exc_info:
        manager.framework_manager.get_framework(fw.framework_id, tenant_id="tenant_tenant2")
    assert "tenant_tenant2" in str(exc_info.value)
    assert "tenant_tenant1" in str(exc_info.value)


def test_flow10_immutable_audit_package(manager):
    """Flow 10: Finalized Audit Package immutability verification."""
    tenant = "tenant_iota"
    pkg = manager.audit_manager.create_audit_package(tenant, "fw_soc2", "bundle_123", "rep_123")
    assert pkg.is_finalized is True
    assert len(pkg.package_fingerprint) == 64  # SHA-256 length

    fetched_pkg = manager.audit_manager.get_audit_package(pkg.package_id, tenant)
    assert fetched_pkg.package_fingerprint == pkg.package_fingerprint


def test_flow11_secret_redaction(manager):
    """Flow 11: Injected API keys, passwords, and PII are redacted from evidence metadata."""
    tenant = "tenant_kappa"
    ev = manager.evidence_manager.collect_evidence(
        tenant_id=tenant,
        subject_type="SERVICE",
        subject_id="srv_01",
        evidence_type=EvidenceType.SECURITY_EVENT,
        source_system=EvidenceSource.IDENTITY_SECURITY_MANAGER,
        source_reference="auth_ref_01",
        metadata={
            "api_key": "sk-secret-key-12345",
            "password": "super-secret-password",
            "user_email": "admin@enterprise.com",
        },
    )
    assert ev.metadata["api_key"] == "[REDACTED]"
    assert ev.metadata["password"] == "[REDACTED]"
    assert ev.metadata["user_email"] == "admin@enterprise.com"


def test_flow12_full_continuous_compliance_lifecycle(manager):
    """Flow 12: Complete Continuous Compliance Lifecycle."""
    tenant = "tenant_lambda"
    # 1. Event/Signal
    sig = manager.monitoring_manager.emit_signal(
        tenant, ComplianceSignalType.SECURITY_EVENT, "IdentitySecurityManager", "user_123"
    )
    # 2. Evidence
    ev = manager.evidence_manager.collect_evidence(
        tenant, "USER", "user_123", EvidenceType.SECURITY_EVENT, EvidenceSource.IDENTITY_SECURITY_MANAGER, sig.signal_id
    )
    # 3. Assessment & Finding
    finding = manager.finding_manager.create_finding(
        tenant, "Unauthorized Auth", "Failed auth attempt", severity=FindingSeverity.HIGH, evidence_ids=[ev.evidence_id]
    )
    # 4. Remediation & Approval
    action = RemediationAction(
        target_subsystem="IdentitySecurityManager", action_type="REVOKE_TOKEN", description="Revoke token"
    )
    plan = manager.remediation_manager.create_remediation_plan(tenant, finding.finding_id, [action], risk_level="HIGH")
    manager.governance_engine.approval_engine.approve(plan.approval_request_id, approver_id="sec_admin")

    # 5. Delegation
    plan.status = RemediationStatus.APPROVED
    manager.remediation_manager.delegate_execution(plan.plan_id, tenant, delegated_subsystem="IdentitySecurityManager")

    # 6. Posture & Assurance & Audit Package
    posture = manager.posture_manager.calculate_posture(tenant)
    assurance = manager.assurance_manager.generate_assurance_report(
        tenant, "fw_soc2", conclusion=AssuranceConclusion.ASSURED
    )
    audit_pkg = manager.audit_manager.create_audit_package(tenant, "fw_soc2", ev.evidence_id, assurance.report_id)

    assert posture.overall_score >= 90.0
    assert assurance.conclusion == AssuranceConclusion.ASSURED
    assert audit_pkg.is_finalized is True
