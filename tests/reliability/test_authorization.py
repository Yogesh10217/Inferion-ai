"""Unit tests for AuthorizationEngine."""

import pytest

from app.security.authorization import AuthorizationEngine
from app.security.exceptions import PermissionDeniedError, TenantAccessDeniedError
from app.security.identity import UserIdentity


def test_tenant_isolation_enforcement():
    authz = AuthorizationEngine()
    user_a = UserIdentity.create(user_id="user_a", tenant_id="tenant_a")

    # Accessing resource in same tenant
    assert authz.validate_tenant_access(user_a, "tenant_a") is True

    # Accessing resource in global tenant
    assert authz.validate_tenant_access(user_a, "global") is True

    # Cross-tenant access attempt must raise TenantAccessDeniedError
    with pytest.raises(TenantAccessDeniedError):
        authz.validate_tenant_access(user_a, "tenant_b")


def test_authorize_permissions_and_scopes():
    authz = AuthorizationEngine()
    user = UserIdentity.create(user_id="user_b", tenant_id="tenant_a", scopes=["read"], permissions=["agents:view"])

    assert authz.authorize(user, required_scopes=["read"], required_permissions=["agents:view"]) is True

    with pytest.raises(PermissionDeniedError):
        authz.authorize(user, required_permissions=["agents:delete"])
