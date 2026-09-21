"""Unit tests for IdentityManager creation and lifecycle status transitions."""

from app.identity.identity import IdentityManager, IdentityStatus, IdentityType


def test_identity_creation_and_status_updates():
    mgr = IdentityManager()

    ident = mgr.create_identity("user_john", identity_type=IdentityType.HUMAN, tenant_id="t_ident", roles=["developer"])
    assert ident.username == "user_john"
    assert ident.identity_type == IdentityType.HUMAN
    assert ident.status == IdentityStatus.ACTIVE

    # Suspend identity
    upd = mgr.update_status(ident.identity_id, IdentityStatus.SUSPENDED)
    assert upd.status == IdentityStatus.SUSPENDED
