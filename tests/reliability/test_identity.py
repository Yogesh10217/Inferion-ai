"""Unit tests for Enterprise Identity models."""

from app.security.identity import SystemIdentity, UserIdentity


def test_user_identity_creation_and_permissions():
    user = UserIdentity.create(
        user_id="user_123",
        tenant_id="tenant_a",
        roles=["developer"],
        permissions=["agents:create", "models:read"],
        scopes=["read", "write"],
    )
    assert user.identity_id == "user:user_123"
    assert user.tenant_id == "tenant_a"
    assert user.has_permission("agents:create") is True
    assert user.has_permission("admin:all") is False
    assert user.has_role("developer") is True
    assert user.has_scope("read") is True


def test_system_identity_admin_bypass():
    sys_identity = SystemIdentity.create("engine_core")
    assert sys_identity.is_admin is True
    assert sys_identity.has_permission("anything") is True
    assert sys_identity.has_role("admin") is True
    assert sys_identity.has_scope("anything") is True
