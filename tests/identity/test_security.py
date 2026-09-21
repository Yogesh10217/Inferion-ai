"""Unit tests for identity security validation."""

from app.identity.access_control import AccessContext, AccessControlManager, AccessDecisionType


def test_cross_tenant_denial_check():
    mgr = AccessControlManager()

    ctx = AccessContext(identity_id="user_tenant_A", role="guest", tenant_id="Tenant_A")
    res = mgr.evaluate_access("admin_override", ctx)

    assert res.decision == AccessDecisionType.DENY
    assert res.allow is False
