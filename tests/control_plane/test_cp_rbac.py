"""Unit tests for RBAC & Administrative Permission enforcement."""

import pytest

from app.security.authorization import AuthorizationEngine
from app.security.exceptions import PermissionDeniedError
from app.security.identity import UserIdentity


def test_administrative_permission_enforcement():
    authz = AuthorizationEngine()
    norm_user = UserIdentity.create(user_id="u_norm", tenant_id="t1", roles=["developer"])
    admin_user = UserIdentity.create(user_id="u_admin", tenant_id="t1", roles=["admin"])

    # Normal user lacks admin permissions
    with pytest.raises(PermissionDeniedError):
        authz.authorize(norm_user, required_roles=["admin"])

    # Admin user passes
    assert authz.authorize(admin_user, required_roles=["admin"]) is True
