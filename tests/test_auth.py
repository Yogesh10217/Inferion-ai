from datetime import timedelta

import pytest

from app.auth.api_key_service import APIKeyService
from app.auth.exceptions import ExpiredTokenException
from app.auth.jwt_service import JWTService
from app.auth.models import User
from app.auth.password_service import PasswordService
from app.core.database import async_session_maker
from app.tenant.models import Membership


def test_password_hashing():
    password = "test_user_password_456"
    hashed = PasswordService.get_password_hash(password)

    assert password != hashed
    assert PasswordService.verify_password(password, hashed)
    assert not PasswordService.verify_password("wrongpassword", hashed)


def test_jwt_creation_and_verification():
    data = {"sub": "user123"}
    token = JWTService.create_access_token(data)

    payload = JWTService.verify_token(token)
    assert payload["sub"] == "user123"
    assert "exp" in payload


def test_jwt_expiry():
    data = {"sub": "user123"}
    token = JWTService.create_access_token(data, expires_delta=timedelta(seconds=-1))

    with pytest.raises(ExpiredTokenException):
        JWTService.verify_token(token)


def test_refresh_token_creation():
    data = {"sub": "user123"}
    token = JWTService.create_refresh_token(data)

    payload = JWTService.verify_token(token)
    assert payload["sub"] == "user123"
    assert payload["type"] == "refresh"


def test_api_key_generation_and_hashing():
    raw_key, prefix, hashed_key = APIKeyService.generate_api_key()
    assert raw_key.startswith("sk_")
    assert prefix == "sk"
    assert len(hashed_key) == 64  # SHA-256 hex digest length

    # Hashing same key produces same hash
    hashed_again = APIKeyService.hash_api_key(raw_key)
    assert hashed_again == hashed_key


@pytest.mark.asyncio
async def test_require_admin_role_enforcement(get_client):
    # Seed a non-admin user in DB with valid membership
    async with async_session_maker() as session:
        non_admin_user = User(
            id="regular_user_auth_test",
            username="regularuser",
            email="regular@test.com",
            password_hash="hash",
            is_admin=False,
            is_active=True,
        )
        membership = Membership(
            organization_id="test_org_id", user_id="regular_user_auth_test", role_id="member", status="active"
        )
        session.add(non_admin_user)
        session.add(membership)
        try:
            await session.commit()
        except Exception:
            await session.rollback()

    non_admin_token = JWTService.create_access_token({"sub": "regular_user_auth_test"})
    headers = {"Authorization": f"Bearer {non_admin_token}", "X-Organization-Id": "test_org_id"}

    async with get_client() as client:
        # Non-admin user trying to access admin endpoint -> 403 Forbidden
        res = await client.get("/v1/admin/users", headers=headers)
        assert res.status_code == 403
        assert "Admin privileges required" in res.json()["detail"]
