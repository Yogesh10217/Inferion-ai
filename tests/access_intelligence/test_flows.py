"""Mandatory E2E Integration Flow Tests for Enterprise AI Access Intelligence (Phase 5.39)."""

import pytest

from app.access_intelligence.access_reviews import AccessReviewDecision, AccessReviewStatus
from app.access_intelligence.anomalies import AccessAnomalySeverity, AccessAnomalyType
from app.access_intelligence.authorization import AuthorizationDecisionOutcome
from app.access_intelligence.certifications import CertificationDecision
from app.access_intelligence.correlation import AccessCorrelationType
from app.access_intelligence.emergency_access import EmergencyAccessReason, EmergencyAccessStatus
from app.access_intelligence.entitlements import EntitlementType
from app.access_intelligence.exceptions import (
    AccessIntelligenceException,
    CrossTenantAccessIntelligenceException,
    HighRiskAccessRequiresApprovalException,
    ImmutableAccessRecordException,
)
from app.access_intelligence.identities import IdentityType
from app.access_intelligence.manager import AccessIntelligenceManager
from app.access_intelligence.privileged_access import PrivilegedAccessScope, PrivilegedAccessStatus
from app.access_intelligence.remediation import AccessRemediationAction
from app.access_intelligence.signals import AccessSignalType
from app.access_intelligence.toxic_combinations import ToxicCombinationSeverity
from app.access_intelligence.verification import VerificationCheck, VerificationStatus


@pytest.fixture
def manager():
    return AccessIntelligenceManager()


def test_flow1_identity_and_entitlement_registration(manager):
    """Flow 1 — Identity and entitlement registration."""
    tenant_id = "tenant_a"
    ident = manager.identity_manager.register_identity(
        tenant_id=tenant_id,
        name="Security Service Account",
        identity_type=IdentityType.SERVICE_IDENTITY,
        external_id="svc_sec_001",
    )
    ent = manager.entitlement_manager.register_entitlement(
        tenant_id=tenant_id,
        code="AUDIT_READ",
        name="Read Audit Logs",
        entitlement_type=EntitlementType.PERMISSION,
        external_entitlement_id="perm_audit_read",
        target_resource_type="AUDIT_LOG",
        target_resource_id="log_001",
        action_type="READ",
    )

    assert ident.tenant_id == tenant_id
    assert ident.identity_type == IdentityType.SERVICE_IDENTITY
    assert ent.code == "AUDIT_READ"
    assert ent.reference.external_entitlement_id == "perm_audit_read"


def test_flow2_access_graph_construction(manager):
    """Flow 2 — Access graph construction."""
    tenant_id = "tenant_a"
    manager.graph_manager.add_node(tenant_id, "ident_01", "IDENTITY", "Human Admin")
    manager.graph_manager.add_node(tenant_id, "role_01", "ROLE", "Production Admin")
    manager.graph_manager.add_node(tenant_id, "res_01", "SENSITIVE_RESOURCE", "Prod Database")

    manager.graph_manager.add_edge(tenant_id, "ident_01", "role_01", "ASSIGNED_ROLE")
    manager.graph_manager.add_edge(tenant_id, "role_01", "res_01", "GRANTED_PERMISSION")

    paths = manager.graph_manager.analyze_paths(tenant_id, "ident_01", "res_01")
    assert len(paths) > 0
    assert paths[0].path_length == 2
    assert paths[0].contains_sensitive_target is True


def test_flow3_least_privilege_violation_detection(manager):
    """Flow 3 — Least privilege violation detection."""
    tenant_id = "tenant_a"
    asm = manager.least_privilege_manager.assess_identity(
        tenant_id=tenant_id,
        identity_id="ident_overpriv",
        assigned_entitlement_ids=["ent_1", "ent_2", "ent_3", "ent_4"],
        used_entitlement_ids=["ent_1"],
        is_production_access=True,
    )

    assert asm.unused_entitlements_count == 3
    assert len(asm.gaps) == 3
    assert asm.privilege_score < 100.0
    assert len(asm.recommendations) == 3
    assert asm.recommendations[0].action_type == "REVOKE_ENTITLEMENT"


def test_flow4_toxic_combination_detection(manager):
    """Flow 4 — Toxic combination detection."""
    tenant_id = "tenant_a"
    findings = manager.toxic_combination_manager.evaluate_identity_entitlements(
        tenant_id=tenant_id,
        identity_id="user_devop",
        active_entitlements=["DEPLOY_RELEASE", "APPROVE_DEPLOYMENT"],
    )

    assert len(findings) == 1
    assert findings[0].rule_code == "SOD-001"
    assert findings[0].severity == ToxicCombinationSeverity.CRITICAL


def test_flow5_high_risk_authorization_blocked(manager):
    """Flow 5 — High-risk authorization blocked."""
    tenant_id = "tenant_a"
    dec = manager.authorization_manager.evaluate_authorization(
        tenant_id=tenant_id,
        subject_identity_id="ident_suspicious",
        action="DISABLE_AUDIT",
        resource_id="prod_audit_stream",
        resource_type="AUDIT_LOG",
        context={"is_blocked": True},
    )

    assert dec.outcome == AuthorizationDecisionOutcome.BLOCK
    assert "blocked" in dec.reason.lower()


def test_flow6_privileged_production_access_requires_approval(manager):
    """Flow 6 — Privileged production access requires approval."""
    tenant_id = "tenant_a"
    req = manager.privileged_access_manager.request_privileged_access(
        tenant_id=tenant_id,
        requester_identity_id="user_engineer",
        target_role_or_entitlement="PROD_DB_ADMIN",
        scope=PrivilegedAccessScope.PRODUCTION,
        justification="Fixing critical DB issue",
    )

    assert req.status == PrivilegedAccessStatus.PENDING_APPROVAL
    assert req.requires_approval is True

    # Activation before approval must raise HighRiskAccessRequiresApprovalException
    with pytest.raises(HighRiskAccessRequiresApprovalException):
        manager.privileged_access_manager.activate_request(tenant_id, req.request_id)

    # Approve and then activate successfully
    manager.privileged_access_manager.approve_request(tenant_id, req.request_id, "approver_manager")
    activated = manager.privileged_access_manager.activate_request(tenant_id, req.request_id)
    assert activated.status == PrivilegedAccessStatus.ACTIVATED


def test_flow7_emergency_access_requires_justification_and_time_bounds(manager):
    """Flow 7 — Emergency access requires justification and time bounds."""
    tenant_id = "tenant_a"

    # Request without detailed justification fails
    with pytest.raises(AccessIntelligenceException):
        manager.emergency_access_manager.request_emergency_access(
            tenant_id=tenant_id,
            requester_identity_id="oncall_eng",
            reason=EmergencyAccessReason.SYSTEM_OUTAGE,
            justification="short",
        )

    # Valid emergency request
    em_req = manager.emergency_access_manager.request_emergency_access(
        tenant_id=tenant_id,
        requester_identity_id="oncall_eng",
        reason=EmergencyAccessReason.SYSTEM_OUTAGE,
        justification="Outage P0 incident #4928 - DB failover required.",
        time_bound_minutes=60,
    )
    assert em_req.status == EmergencyAccessStatus.REQUESTED
    assert em_req.audit_fingerprint != ""

    activated = manager.emergency_access_manager.activate_emergency_access(tenant_id, em_req.request_id)
    assert activated.status == EmergencyAccessStatus.ACTIVE
    assert activated.expires_at is not None


def test_flow8_access_anomaly_detection(manager):
    """Flow 8 — Access anomaly detection."""
    tenant_id = "tenant_a"
    sig = manager.signal_manager.ingest_signal(
        tenant_id=tenant_id,
        signal_type=AccessSignalType.PRIVILEGED_ACTION,
        source_telemetry_ref="tel_999",
        subject_identity_id="ident_dormant",
    )

    anom = manager.anomaly_manager.detect_anomaly(
        tenant_id=tenant_id,
        subject_identity_id="ident_dormant",
        anomaly_type=AccessAnomalyType.DORMANT_IDENTITY_ACTIVATION,
        title="Dormant Account Active",
        description="Identity inactive for 180 days suddenly requested admin elevation.",
        source_signal_id=sig.signal_id,
    )

    assert anom.anomaly_type == AccessAnomalyType.DORMANT_IDENTITY_ACTIVATION
    assert anom.severity == AccessAnomalySeverity.HIGH
    assert anom.evidence.source_signal_id == sig.signal_id


def test_flow9_cross_platform_access_correlation(manager):
    """Flow 9 — Cross-platform access correlation."""
    tenant_id = "tenant_a"
    corr = manager.correlation_manager.correlate_event(
        tenant_id=tenant_id,
        correlation_type=AccessCorrelationType.SECURITY_INCIDENT_ACCESS,
        subject_identity_id="ident_compromised",
        external_entity_id="inc_sec_991",
        description="Correlated credential access with active security incident.",
        correlated_resource_ids=["res_vault_01"],
    )

    assert corr.correlation_type == AccessCorrelationType.SECURITY_INCIDENT_ACCESS
    assert corr.external_entity_id == "inc_sec_991"
    assert "res_vault_01" in corr.evidence.correlated_resource_ids


def test_flow10_access_review_lifecycle(manager):
    """Flow 10 — Access review lifecycle."""
    tenant_id = "tenant_a"
    rev = manager.review_manager.create_review(
        tenant_id=tenant_id,
        title="Quarterly IAM Review",
        reviewer_identity_id="manager_alice",
        target_identity_id="user_bob",
        target_entitlement_id="ent_admin",
    )
    assert rev.status == AccessReviewStatus.DRAFT

    manager.review_manager.activate_review(tenant_id, rev.review_id)
    manager.review_manager.start_reviewing(tenant_id, rev.review_id)
    manager.review_manager.record_decision(
        tenant_id, rev.review_id, AccessReviewDecision.REVOKE, "Role no longer needed"
    )
    finalized = manager.review_manager.finalize_review(tenant_id, rev.review_id)

    assert finalized.status == AccessReviewStatus.FINALIZED
    assert finalized.is_finalized is True

    # Mutating finalized review raises ImmutableAccessRecordException
    with pytest.raises(ImmutableAccessRecordException):
        manager.review_manager.record_decision(
            tenant_id, rev.review_id, AccessReviewDecision.MAINTAIN, "Attempt change"
        )


def test_flow11_immutable_finalized_certification(manager):
    """Flow 11 — Immutable finalized certification."""
    tenant_id = "tenant_a"
    cert = manager.certification_manager.create_certification(
        tenant_id=tenant_id,
        name="SOC2 Annual Entitlement Certification",
        certifier_identity_id="auditor_jane",
    )

    manager.certification_manager.start_certification(tenant_id, cert.certification_id)
    manager.certification_manager.record_decision(tenant_id, cert.certification_id, CertificationDecision.CERTIFIED)
    finalized = manager.certification_manager.finalize_certification(tenant_id, cert.certification_id)

    assert finalized.is_finalized is True
    assert finalized.fingerprint != ""

    with pytest.raises(ImmutableAccessRecordException):
        manager.certification_manager.record_decision(
            tenant_id, cert.certification_id, CertificationDecision.REVOCATION_REQUIRED
        )


def test_flow12_delegation_only_remediation_enforcement(manager):
    """Flow 12 — Delegation-only remediation enforcement."""
    tenant_id = "tenant_a"
    plan = manager.remediation_manager.create_remediation_plan(
        tenant_id=tenant_id,
        target_identity_id="ident_overprivileged",
        action=AccessRemediationAction.REVOKE_ENTITLEMENT,
        target_entitlement_id="ent_unneeded",
    )

    del_req = manager.remediation_manager.delegate_remediation(tenant_id, plan.plan_id)
    assert del_req.action == "ACCESS_REMEDIATION_REVOKE_ENTITLEMENT"
    assert del_req.payload["target_entitlement_id"] == "ent_unneeded"


def test_flow13_remediation_verification_failure(manager):
    """Flow 13 — Remediation verification failure."""
    tenant_id = "tenant_a"
    verif = manager.verification_manager.verify_remediation(
        tenant_id=tenant_id,
        remediation_plan_id="rem_plan_100",
        checks=[
            VerificationCheck(
                target_resource_id="ent_100", expected_state="REVOKED", observed_state="ACTIVE", passed=False
            )
        ],
        notes="Permission still active in cloud provider",
    )

    assert verif.status == VerificationStatus.FAILURE
    assert verif.checks[0].passed is False


def test_flow14_cross_tenant_access_blocked(manager):
    """Flow 14 — Cross-tenant access blocked with zero metadata leakage."""
    tenant_id_a = "tenant_a"
    tenant_id_b = "tenant_b"

    ident = manager.identity_manager.register_identity(
        tenant_id=tenant_id_a,
        name="Tenant A Secret Agent",
        identity_type=IdentityType.AGENT,
        external_id="ext_a",
    )

    with pytest.raises(CrossTenantAccessIntelligenceException) as exc_info:
        manager.identity_manager.get_identity(tenant_id_b, ident.identity_id)

    assert "Access denied." in str(exc_info.value)
    assert tenant_id_a not in str(exc_info.value)
    assert ident.identity_id not in str(exc_info.value)


def test_flow15_sensitive_data_redaction(manager):
    """Flow 15 — Sensitive data redaction."""
    tenant_id = "tenant_a"
    raw_payload = {
        "user_email": "admin@enterprise.com",
        "api_token": "sk-secret-key-12345",
        "action": "AUTHORIZATION_CHECK",
    }

    sig = manager.signal_manager.ingest_signal(
        tenant_id=tenant_id,
        signal_type=AccessSignalType.AUDIT_EVENT,
        source_telemetry_ref="telemetry_raw_01",
        subject_identity_id="ident_user",
        raw_metadata=raw_payload,
    )

    assert "api_token" not in sig.sanitized_metadata or sig.sanitized_metadata["api_token"] != "sk-secret-key-12345"


def test_flow16_immutable_access_evidence_bundle(manager):
    """Flow 16 — Immutable access evidence bundle."""
    tenant_id = "tenant_a"
    bundle = manager.evidence_manager.create_bundle(tenant_id, "Q3 Audit Evidence")
    manager.evidence_manager.add_evidence(tenant_id, bundle.bundle_id, "AUTH_RECORD", "rec_01", {"status": "ALLOW"})
    finalized = manager.evidence_manager.finalize_bundle(tenant_id, bundle.bundle_id)

    assert finalized.is_finalized is True
    assert finalized.integrity is not None
    assert manager.evidence_manager.verify_bundle_integrity(tenant_id, bundle.bundle_id) is True

    with pytest.raises(ImmutableAccessRecordException):
        manager.evidence_manager.add_evidence(tenant_id, bundle.bundle_id, "AUTH_RECORD", "rec_02", {"status": "DENY"})


def test_flow17_high_risk_entitlement_remediation_requires_approval(manager):
    """Flow 17 — High-risk entitlement remediation requires approval."""
    tenant_id = "tenant_a"
    plan = manager.remediation_manager.create_remediation_plan(
        tenant_id=tenant_id,
        target_identity_id="service_account_prod",
        action=AccessRemediationAction.REVOKE_ENTITLEMENT,
        target_entitlement_id="ent_prod_db_rw",
        requires_approval=True,
    )

    # Delegating without approval must raise HighRiskAccessRequiresApprovalException
    with pytest.raises(HighRiskAccessRequiresApprovalException):
        manager.remediation_manager.delegate_remediation(tenant_id, plan.plan_id)

    manager.remediation_manager.approve_remediation(tenant_id, plan.plan_id, "approval_sec_officer")
    del_req = manager.remediation_manager.delegate_remediation(tenant_id, plan.plan_id)
    assert del_req.action == "ACCESS_REMEDIATION_REVOKE_ENTITLEMENT"


def test_flow18_access_investigation_snapshot_generation(manager):
    """Flow 18 — Access investigation snapshot generation."""
    tenant_id = "tenant_a"
    inv = manager.investigation_manager.open_investigation(tenant_id, "Breach Risk Investigation", "user_malicious")
    manager.investigation_manager.start_investigating(tenant_id, inv.investigation_id)
    manager.investigation_manager.record_finding(tenant_id, inv.investigation_id, "Unusual data egress", "CRITICAL")

    concluded = manager.investigation_manager.conclude_investigation(tenant_id, inv.investigation_id)
    assert concluded.is_concluded is True
    assert concluded.snapshot_id is not None


def test_flow19_learning_recommendations_do_not_automatically_modify_privileges(manager):
    """Flow 19 — Learning recommendations do not automatically modify privileges."""
    tenant_id = "tenant_a"
    rec = manager.learning_manager.record_access_pattern(
        tenant_id=tenant_id,
        identity_id="agent_assistant",
        pattern_name="High-Frequency Admin Tool Use",
        description="Agent calls admin tools repeatedly.",
        recommended_action="REVIEW_TOOL_PERMISSIONS",
        reasoning="Prevent potential agent loop or privilege abuse.",
    )

    assert len(rec.recommendations) == 1
    assert rec.recommendations[0].auto_execute is False


def test_flow20_full_enterprise_access_intelligence_lifecycle(manager):
    """Flow 20 — Full enterprise access intelligence lifecycle."""
    tenant_id = "tenant_enterprise"
    result = manager.run_full_lifecycle(tenant_id, "enterprise_agent_x")

    assert result["status"] == "COMPLETED"
    assert result["authorization_outcome"] == "ALLOW"
    assert result["governance_status"] == "ALLOW"
    assert result["snapshot_id"] is not None
    assert result["delegation_id"] is not None
    assert result["evidence_hash"] is not None
