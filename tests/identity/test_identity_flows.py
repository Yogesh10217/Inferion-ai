"""Mandatory End-to-End Integration Flow Tests for Phase 5.17 Identity, Access & Zero-Trust Security Platform."""

import pytest
from app.identity.manager import IdentitySecurityManager
from app.identity.identity import IdentityType
from app.identity.authentication import AuthenticationMethod, AuthenticationAssuranceLevel
from app.identity.access_control import AccessContext, AccessDecisionType
from app.identity.privileged_access import PrivilegedRole, PrivilegedAccessStatus
from app.identity.zero_trust import ZeroTrustAction, TrustLevel
from app.identity.risk import AnomalyType, IdentityRiskSeverity
from app.identity.credentials import CredentialType, CredentialStatus
from app.identity.exceptions import AgentBoundaryViolationException, SessionRevokedException


def test_e2e_flow_1_high_risk_privileged_access():
    """Flow 1 — High-Risk Privileged Access: JIT request -> Approval -> Temporary Grant -> Audit."""
    mgr = IdentitySecurityManager()

    # 1. Identity verified
    ident = mgr.identity_manager.create_identity("admin_db", identity_type=IdentityType.ADMINISTRATOR, tenant_id="t_flow1")

    # 2. Authentication assurance evaluated
    auth_res = mgr.auth_manager.authenticate(ident.identity_id, method=AuthenticationMethod.MFA, mfa_verified=True, tenant_id="t_flow1")
    assert auth_res.assurance_level == AuthenticationAssuranceLevel.HIGH

    # 3. Zero Trust evaluation -> LOW_RISK / HIGH_RISK
    zt_res = mgr.zero_trust_engine.evaluate(ident.identity_id, tenant_id="t_flow1", risk_score=50.0)
    assert zt_res.recommended_action in (ZeroTrustAction.REQUIRE_MFA, ZeroTrustAction.RESTRICT, ZeroTrustAction.MONITOR)

    # 4. Request JIT Privileged Access
    grant = mgr.privileged_access_manager.request_privileged_access(ident.identity_id, PrivilegedRole.DATABASE_ADMIN, tenant_id="t_flow1", duration_minutes=15)
    assert grant.status == PrivilegedAccessStatus.REQUESTED
    assert grant.approval_request_id is not None

    # 5. Administrator Approval -> Active Grant
    appr_grant = mgr.privileged_access_manager.approve_grant(grant.grant_id)
    assert appr_grant.status == PrivilegedAccessStatus.ACTIVE
    assert mgr.privileged_access_manager.check_grant_validity(grant.grant_id) is True

    # 6. Immutable Audit Log
    aud_evt = mgr.audit_manager.record_event("PRIVILEGED_ACCESS", ident.identity_id, "db_access", grant.grant_id, "GRANTED", tenant_id="t_flow1")
    assert aud_evt.outcome == "GRANTED"


def test_e2e_flow_2_suspicious_session():
    """Flow 2 — Suspicious Session: Unusual IP -> IdentityRiskEngine -> Restricted Session -> Ops Incident."""
    mgr = IdentitySecurityManager()

    ident = mgr.identity_manager.create_identity("user_suspicious", tenant_id="t_flow2")
    sess = mgr.session_manager.create_session(ident.identity_id, tenant_id="t_flow2")

    # 1. Detect unusual IP anomaly -> Risk = HIGH
    risk_evt = mgr.identity_risk_engine.record_risk_event(
        identity_id=ident.identity_id,
        anomaly_type=AnomalyType.UNUSUAL_IP,
        severity=IdentityRiskSeverity.HIGH,
        description="Login attempt from unauthorized country IP",
        tenant_id="t_flow2",
    )
    assert risk_evt.incident_id is not None  # Auto Operations Incident created!

    # 2. Automatically restrict session
    r_sess = mgr.session_manager.restrict_session(sess.session_id, reason="HIGH risk anomaly detected")
    assert r_sess.is_restricted is True

    # 3. Zero Trust evaluation -> RESTRICT or TERMINATE_SESSION action
    zt_res = mgr.zero_trust_engine.evaluate(ident.identity_id, tenant_id="t_flow2", network_trusted=False, risk_score=50.0)
    assert zt_res.recommended_action in (ZeroTrustAction.RESTRICT, ZeroTrustAction.TERMINATE_SESSION)



def test_e2e_flow_3_agent_delegated_authorization():
    """Flow 3 — Agent Delegated Authorization: Delegated scope boundary enforcement."""
    mgr = IdentitySecurityManager()

    user = mgr.identity_manager.create_identity("user_delegator", tenant_id="t_flow3")

    # 1. Authorize AI Agent with scoped permissions
    del_auth = mgr.agent_identity_manager.create_delegated_authorization(
        user_identity_id=user.identity_id,
        agent_id="agent_assistant",
        delegated_scopes=["read", "search"],
        tenant_id="t_flow3",
    )

    # 2. Allowed scope execution -> Success
    assert mgr.agent_identity_manager.validate_agent_action(del_auth.delegation_id, "search_docs", requested_scope="search") is True

    # 3. Action exceeding delegated boundary -> Exception!
    with pytest.raises(AgentBoundaryViolationException):
        mgr.agent_identity_manager.validate_agent_action(del_auth.delegation_id, "export_full_database", requested_scope="export")


def test_e2e_flow_4_credential_rotation():
    """Flow 4 — Credential Rotation: Service credential rotation & audit trail."""
    mgr = IdentitySecurityManager()

    cred = mgr.credential_manager.create_credential("Payment Gateway API Key", identity_id="service_pay", credential_type=CredentialType.API_KEY, tenant_id="t_flow4")
    assert cred.status == CredentialStatus.ACTIVE

    # Rotate Credential
    new_cred = mgr.credential_manager.rotate_credential(cred.credential_id)
    assert mgr.credential_manager.get_credential(cred.credential_id).status == CredentialStatus.ROTATED
    assert new_cred.status == CredentialStatus.ACTIVE

    # Record Audit
    aud = mgr.audit_manager.record_event("TOKEN_ROTATION", "service_pay", "rotate_key", new_cred.credential_id, "ROTATED", tenant_id="t_flow4")
    assert aud.event_type == "TOKEN_ROTATION"


def test_e2e_flow_5_continuous_authorization():
    """Flow 5 — Continuous Authorization: Dynamic risk increase restricts ongoing access."""
    mgr = IdentitySecurityManager()

    # Initial access allowed
    ctx_init = AccessContext(identity_id="user_ca", role="analyst", risk_score=10.0)
    dec_init = mgr.access_control_manager.evaluate_access("read", ctx_init)
    assert dec_init.decision == AccessDecisionType.ALLOW

    # Risk increases mid-session -> Require approval
    ctx_high = AccessContext(identity_id="user_ca", role="analyst", risk_score=85.0)
    dec_high = mgr.access_control_manager.evaluate_access("read", ctx_high)
    assert dec_high.decision == AccessDecisionType.REQUIRE_APPROVAL
    assert dec_high.approval_request_id is not None

    # Deterministic explanation generated
    expl = mgr.explainability_engine.explain_access_decision("read", ctx_high, dec_high)
    assert expl.is_deterministic is True
    assert "REQUIRE_APPROVAL" in expl.outcome


def test_e2e_flow_6_compromised_credential():
    """Flow 6 — Compromised Credential: Critical anomaly -> Revoke credential & kill session."""
    mgr = IdentitySecurityManager()

    ident = mgr.identity_manager.create_identity("user_comp", tenant_id="t_flow6")
    sess = mgr.session_manager.create_session(ident.identity_id, tenant_id="t_flow6")
    cred = mgr.credential_manager.create_credential("User Token", identity_id=ident.identity_id, tenant_id="t_flow6")

    # Critical Anomaly Detected
    risk_evt = mgr.identity_risk_engine.record_risk_event(
        identity_id=ident.identity_id,
        anomaly_type=AnomalyType.TOKEN_ABUSE,
        severity=IdentityRiskSeverity.CRITICAL,
        description="Stolen token replay attack detected",
        tenant_id="t_flow6",
    )
    assert risk_evt.incident_id is not None

    # Revoke Credential & Terminate Session
    mgr.credential_manager.revoke_credential(cred.credential_id, reason="Compromised token")
    mgr.session_manager.revoke_session(sess.session_id, reason="Security breach")

    assert mgr.credential_manager.get_credential(cred.credential_id).status == CredentialStatus.REVOKED
    with pytest.raises(SessionRevokedException):
        mgr.session_manager.get_session(sess.session_id)


def test_e2e_flow_7_tenant_isolation():
    """Flow 7 — Tenant Isolation: Tenant A identity resources strictly isolated from Tenant B."""
    mgr = IdentitySecurityManager()

    # Tenant A Setup
    id_A = mgr.identity_manager.create_identity("user_A", tenant_id="Tenant_A")
    sess_A = mgr.session_manager.create_session(id_A.identity_id, tenant_id="Tenant_A")
    cred_A = mgr.credential_manager.create_credential("cred_A", identity_id=id_A.identity_id, tenant_id="Tenant_A")

    # Tenant B Setup
    id_B = mgr.identity_manager.create_identity("user_B", tenant_id="Tenant_B")
    sess_B = mgr.session_manager.create_session(id_B.identity_id, tenant_id="Tenant_B")
    cred_B = mgr.credential_manager.create_credential("cred_B", identity_id=id_B.identity_id, tenant_id="Tenant_B")

    # Cross-tenant query checks
    idents_A = mgr.identity_manager.list_identities("Tenant_A")
    idents_B = mgr.identity_manager.list_identities("Tenant_B")
    assert len(idents_A) == 1 and idents_A[0].identity_id == id_A.identity_id
    assert len(idents_B) == 1 and idents_B[0].identity_id == id_B.identity_id

    sessions_A = mgr.session_manager.list_sessions("Tenant_A")
    assert len(sessions_A) == 1 and sessions_A[0].session_id == sess_A.session_id
