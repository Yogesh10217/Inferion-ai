"""Mandatory 20 End-to-End Test Flows for Phase 5.48 Identity Assurance Platform."""

import pytest

from app.identity_assurance.access_graph import AccessGraphNode
from app.identity_assurance.anomalies import IdentityAnomalyType
from app.identity_assurance.evidence import IdentityEvidence
from app.identity_assurance.exceptions import (
    CrossTenantIdentityAssuranceException,
    ImmutableIdentityRecordException,
)
from app.identity_assurance.governance import IdentityGovernanceOutcome, IdentityGovernanceRequest
from app.identity_assurance.identities import IdentityCategory, IdentityType
from app.identity_assurance.manager import IdentityAssuranceManager
from app.identity_assurance.remediation import IdentityRemediationAction
from app.identity_assurance.signals import IdentitySignalSource, IdentitySignalType


@pytest.fixture
def manager() -> IdentityAssuranceManager:
    return IdentityAssuranceManager()


def test_flow_01_identity_registration_and_tenant_isolation(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Alice Admin",
        identity_type=IdentityType.HUMAN,
        category=IdentityCategory.EMPLOYEE,
    )
    assert identity.identity_id is not None
    assert identity.tenant_id == tenant_id
    assert identity.name == "Alice Admin"

    retrieved = manager.get_identity(tenant_id, identity.identity_id)
    assert retrieved.identity_id == identity.identity_id


def test_flow_02_cross_tenant_access_blocked_zero_metadata_leakage(manager: IdentityAssuranceManager):
    tenant_a = "tenant-alpha"
    tenant_b = "tenant-beta"

    identity = manager.register_identity(
        tenant_id=tenant_a,
        name="Secret Identity",
        identity_type=IdentityType.HUMAN,
    )

    with pytest.raises(CrossTenantIdentityAssuranceException) as exc_info:
        manager.get_identity(tenant_b, identity.identity_id)

    msg = str(exc_info.value)
    # Verify ZERO metadata leakage
    assert tenant_a not in msg
    assert identity.identity_id not in msg
    assert "Secret Identity" not in msg


def test_flow_03_identity_profile_assessment(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Bob Engineer",
        identity_type=IdentityType.HUMAN,
    )
    profile = manager.profile_manager.get_profile(tenant_id, identity.identity_id)
    assert profile.identity_id == identity.identity_id
    assert profile.tenant_id == tenant_id
    assert profile.criticality in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def test_flow_04_identity_trust_assessment(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Trust Test Identity",
        identity_type=IdentityType.HUMAN,
    )
    trust = manager.trust_engine.assess_trust(tenant_id, identity.identity_id, mfa_enabled=True)
    assert trust.is_trusted is True
    assert trust.trust_score.overall_trust_score >= 0.70

    platform_trust = manager.trust_engine.to_platform_trust_assessment(trust)
    assert platform_trust.target_resource_id == identity.identity_id


def test_flow_05_authentication_posture_intelligence(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Service Bot",
        identity_type=IdentityType.SERVICE,
    )
    auth = manager.auth_manager.assess_authentication(tenant_id, identity.identity_id, mfa_enabled=False)
    assert auth.mfa_enabled is False
    assert auth.risk.has_anomaly is True


def test_flow_06_authorization_scope_analysis(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Auth Scope Identity",
        identity_type=IdentityType.HUMAN,
    )
    auth_scope = manager.authorization_manager.assess_authorization(
        tenant_id=tenant_id,
        identity_id=identity.identity_id,
        permissions=["data:read", "data:write"],
    )
    assert auth_scope.total_permissions == 2
    assert auth_scope.exposure_score > 0.0


def test_flow_07_privilege_risk_detection(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Super User",
        identity_type=IdentityType.HUMAN,
    )
    priv = manager.privilege_manager.assess_privileges(tenant_id, identity.identity_id)
    assert priv.risk.risk_score >= 0.0
    assert priv.identity_id == identity.identity_id


def test_flow_08_least_privilege_recommendation(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Overprivileged User",
        identity_type=IdentityType.HUMAN,
    )
    active_perms = ["read:all", "write:all", "delete:all", "admin:exec"]
    used_perms = ["read:all"]
    least_priv = manager.least_privilege_manager.assess_least_privilege(
        tenant_id, identity.identity_id, active_perms, used_perms
    )
    assert len(least_priv.recommendations) == 3
    # Enforce auto_execute = False
    assert all(r.auto_execute is False for r in least_priv.recommendations)


def test_flow_09_access_pattern_intelligence(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Pattern User",
        identity_type=IdentityType.HUMAN,
    )
    patterns = manager.access_pattern_manager.assess_patterns(tenant_id, identity.identity_id)
    assert patterns.identity_id == identity.identity_id
    assert patterns.risk_score >= 0.0


def test_flow_10_behavior_anomaly_detection(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Anomalous Agent",
        identity_type=IdentityType.AGENT,
    )
    anomaly = manager.anomaly_manager.detect_anomaly(
        tenant_id=tenant_id,
        identity_id=identity.identity_id,
        anomaly_type=IdentityAnomalyType.ABNORMAL_AGENT_ACTIVITY,
    )
    assert anomaly.anomaly_id is not None
    assert anomaly.anomaly_type == IdentityAnomalyType.ABNORMAL_AGENT_ACTIVITY


def test_flow_11_privilege_creep_detection(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Veteran Employee",
        identity_type=IdentityType.HUMAN,
    )
    creep = manager.privilege_creep_manager.assess_privilege_creep(
        tenant_id=tenant_id,
        identity_id=identity.identity_id,
        initial_count=5,
        current_count=25,
    )
    assert creep.risk.has_creep is True
    assert creep.growth.growth_rate > 1.0


def test_flow_12_toxic_privilege_combination_detection(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Risky User",
        identity_type=IdentityType.HUMAN,
    )
    active_perms = ["data:write", "audit:delete"]
    toxic = manager.toxic_combination_manager.assess_toxic_combinations(tenant_id, identity.identity_id, active_perms)
    assert toxic.risk.has_toxic_combination is True
    assert len(toxic.risk.detected_combinations) > 0


def test_flow_13_segregation_of_duties_conflict(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Conflicting Dev",
        identity_type=IdentityType.HUMAN,
    )
    sod = manager.segregation_manager.assess_segregation(
        tenant_id, identity.identity_id, assigned_roles=["Developer", "ReleaseManager"]
    )
    assert sod.has_conflict is True
    assert len(sod.conflicts) > 0


def test_flow_14_access_graph_traversal_and_risky_access_path(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Graph User",
        identity_type=IdentityType.HUMAN,
    )

    manager.access_graph_manager.add_node(
        tenant_id, AccessGraphNode(node_id=identity.identity_id, node_type="IDENTITY", label=identity.name)
    )
    traversal = manager.access_graph_manager.traverse_access_path(tenant_id, identity.identity_id, "critical-data")
    assert len(traversal.path) > 0

    path_assessment = manager.access_path_manager.analyze_paths(tenant_id, identity.identity_id)
    assert len(path_assessment.paths) > 0


def test_flow_15_high_risk_privileged_action_requires_approval(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Escalating Admin",
        identity_type=IdentityType.HUMAN,
    )

    req = IdentityGovernanceRequest(
        tenant_id=tenant_id,
        action_type="ADMIN_ROLE_ASSIGNMENT",
        target_identity_id=identity.identity_id,
    )
    res = manager.governance_engine.evaluate_action(req)
    assert res.outcome == IdentityGovernanceOutcome.REQUIRE_APPROVAL
    assert res.requires_human_approval is True


def test_flow_16_delegation_only_execution_enforcement(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Remediation Target",
        identity_type=IdentityType.HUMAN,
    )

    action = IdentityRemediationAction(
        action_type="REVOKE_UNUSED_ROLE",
        target_identity_id=identity.identity_id,
        description="Revoke unused role via delegation",
    )
    plan = manager.remediation_manager.plan_remediation(tenant_id, identity.identity_id, [action])
    assert len(plan.delegation_requests) == 1
    assert plan.delegation_requests[0].target.value == "APPLICATION_PLATFORM"


def test_flow_17_sensitive_metadata_sanitization(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Secret User",
        identity_type=IdentityType.HUMAN,
    )

    signal = manager.signal_manager.emit_signal(
        tenant_id=tenant_id,
        identity_id=identity.identity_id,
        signal_type=IdentitySignalType.ACCESS_VIOLATION,
        source=IdentitySignalSource.SECURITY_INTELLIGENCE,
        payload={"password": "SecretPassword123!", "api_key": "sk-test-12345", "user_id": "u-123"},
    )
    # Verify password & api_key sanitized
    assert "password" not in signal.payload or signal.payload["password"] == "[REDACTED]"
    assert "api_key" not in signal.payload or signal.payload["api_key"] == "[REDACTED]"


def test_flow_18_immutable_sha256_evidence_verification(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Evidence User",
        identity_type=IdentityType.HUMAN,
    )

    item = IdentityEvidence(evidence_type="MFA_LOG", source="auth0", payload={"event": "login"})
    bundle = manager.evidence_manager.create_evidence_bundle(tenant_id, identity.identity_id, [item])
    assert bundle.integrity.checksum is not None
    assert bundle.is_finalized is True

    valid = manager.evidence_manager.verify_integrity(tenant_id, bundle.bundle_id)
    assert valid is True

    with pytest.raises(ImmutableIdentityRecordException):
        manager.evidence_manager.finalize_bundle(bundle)


def test_flow_19_learning_does_not_auto_execute(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Learner User",
        identity_type=IdentityType.HUMAN,
    )

    rec_record = manager.learning_manager.generate_recommendations(tenant_id, identity.identity_id)
    assert len(rec_record.recommendations) > 0
    # Mandatory invariant: auto_execute = False
    assert all(r.auto_execute is False for r in rec_record.recommendations)


def test_flow_20_full_enterprise_identity_assurance_lifecycle(manager: IdentityAssuranceManager):
    tenant_id = "tenant-alpha"

    # 1. Register identity
    identity = manager.register_identity(
        tenant_id=tenant_id,
        name="Full Lifecycle Identity",
        identity_type=IdentityType.AGENT,
        category=IdentityCategory.AI_AGENT,
    )
    assert identity.identity_id is not None

    # 2. Assess profile & trust
    profile = manager.profile_manager.get_profile(tenant_id, identity.identity_id)
    trust = manager.trust_engine.assess_trust(tenant_id, identity.identity_id)
    assert profile.identity_id == identity.identity_id
    assert trust.is_trusted is True

    # 3. Assess authentication & authorization
    manager.auth_manager.assess_authentication(tenant_id, identity.identity_id)
    manager.authorization_manager.assess_authorization(tenant_id, identity.identity_id)

    # 4. Privileges & Least privilege
    manager.privilege_manager.assess_privileges(tenant_id, identity.identity_id)
    manager.least_privilege_manager.assess_least_privilege(
        tenant_id, identity.identity_id, ["agent:exec", "data:read"], ["data:read"]
    )

    # 5. Access patterns & Anomaly detection
    manager.access_pattern_manager.assess_patterns(tenant_id, identity.identity_id)
    manager.anomaly_manager.detect_anomaly(
        tenant_id, identity.identity_id, IdentityAnomalyType.ABNORMAL_AGENT_ACTIVITY
    )

    # 6. Risk & Impact
    manager.risk_manager.assess_risk(tenant_id, identity.identity_id)
    manager.impact_manager.assess_impact(tenant_id, identity.identity_id)

    # 7. Governance action evaluation
    gov_req = IdentityGovernanceRequest(
        tenant_id=tenant_id,
        action_type="AGENT_PRIVILEGE_EXPANSION",
        target_identity_id=identity.identity_id,
    )
    gov_res = manager.governance_engine.evaluate_action(gov_req)
    assert gov_res.outcome == IdentityGovernanceOutcome.REQUIRE_APPROVAL

    # 8. Investigation & Snapshot
    inv = manager.investigation_manager.create_investigation(tenant_id, identity.identity_id)
    snapshot = manager.investigation_manager.conclude_investigation(tenant_id, inv.investigation_id, [])
    assert snapshot.metadata.snapshot_id is not None

    # 9. Remediation & Delegation
    rem_action = IdentityRemediationAction(
        action_type="RESTRICT_AGENT_SCOPE",
        target_identity_id=identity.identity_id,
    )
    rem_plan = manager.remediation_manager.plan_remediation(tenant_id, identity.identity_id, [rem_action])
    assert len(rem_plan.delegation_requests) == 1

    # 10. Evidence & Assurance Score
    item = IdentityEvidence(evidence_type="LIFECYCLE_LOG", source="audit", payload={"status": "complete"})
    manager.evidence_manager.create_evidence_bundle(tenant_id, identity.identity_id, [item])
    score = manager.evaluate_identity_assurance(tenant_id, identity.identity_id)
    assert score.overall_assurance_score > 0.0

    # 11. Analytics Report
    report = manager.analytics_engine.generate_report(tenant_id)
    assert report.tenant_id == tenant_id
