"""Unit tests for Just-In-Time (JIT) privileged access management."""

from app.identity.privileged_access import PrivilegedAccessManager, PrivilegedAccessStatus, PrivilegedRole


def test_jit_privileged_access_lifecycle():
    mgr = PrivilegedAccessManager()

    grant = mgr.request_privileged_access("admin_user", PrivilegedRole.DATABASE_ADMIN, duration_minutes=30)
    assert grant.status == PrivilegedAccessStatus.REQUESTED
    assert grant.approval_request_id is not None

    # Approve grant
    appr_grant = mgr.approve_grant(grant.grant_id)
    assert appr_grant.status == PrivilegedAccessStatus.ACTIVE
    assert mgr.check_grant_validity(grant.grant_id) is True

    # Revoke grant
    rev_grant = mgr.revoke_grant(grant.grant_id)
    assert rev_grant.status == PrivilegedAccessStatus.REVOKED
    assert mgr.check_grant_validity(grant.grant_id) is False
