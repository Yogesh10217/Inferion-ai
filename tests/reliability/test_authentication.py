"""Unit tests for AuthenticationManager."""

import pytest

from app.auth.jwt_service import JWTService
from app.security.authentication import AuthenticationManager
from app.security.exceptions import InvalidTokenError


def test_jwt_authentication():
    auth_mgr = AuthenticationManager()
    token = JWTService.create_access_token({"sub": "user_456", "tenant_id": "tenant_b", "roles": ["user"]})

    identity = auth_mgr.authenticate_jwt(token)
    assert identity.user_id == "user_456"
    assert identity.tenant_id == "tenant_b"
    assert identity.has_role("user") is True


def test_jwt_revocation():
    auth_mgr = AuthenticationManager()
    token = JWTService.create_access_token({"sub": "user_789", "tenant_id": "tenant_b"})

    auth_mgr.revoke_token(token)
    with pytest.raises(InvalidTokenError):
        auth_mgr.authenticate_jwt(token)


def test_service_authentication():
    auth_mgr = AuthenticationManager()
    token = auth_mgr.register_service_token(service_id="service_a", service_secret="secret123")

    identity = auth_mgr.authenticate_service(token)
    assert identity.service_id == "service_a"
    assert identity.authentication_method.value == "service"
