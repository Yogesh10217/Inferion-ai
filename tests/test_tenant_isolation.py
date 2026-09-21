import pytest

from app.auth.api_key_service import APIKeyService
from app.auth.jwt_service import JWTService
from app.auth.models import APIKey, Role, User
from app.core.database import async_session_maker
from app.tenant.models import Membership, Organization


@pytest.mark.asyncio
async def test_tenant_isolation_organization_boundaries(get_client):
    # Seed Org A and Org B in DB
    async with async_session_maker() as session:
        user_a = User(id="user_tenant_a", username="usera", email="a@test.com", password_hash="hash", is_admin=False)
        user_b = User(id="user_tenant_b", username="userb", email="b@test.com", password_hash="hash", is_admin=False)
        org_a = Organization(id="org_isolation_a", name="Org A", slug="org-a")
        org_b = Organization(id="org_isolation_b", name="Org B", slug="org-b")
        role_admin = Role(id="admin", name="Admin", description="Admin Role")

        mem_a = Membership(user_id="user_tenant_a", organization_id="org_isolation_a", role_id="admin", status="active")
        mem_b = Membership(user_id="user_tenant_b", organization_id="org_isolation_b", role_id="admin", status="active")

        for item in [role_admin, user_a, user_b, org_a, org_b, mem_a, mem_b]:
            await session.merge(item)
        await session.commit()

    token_a = JWTService.create_access_token({"sub": "user_tenant_a"})
    headers_a = {"Authorization": f"Bearer {token_a}", "X-Organization-Id": "org_isolation_a"}

    token_b = JWTService.create_access_token({"sub": "user_tenant_b"})
    headers_b_fake_a = {"Authorization": f"Bearer {token_b}", "X-Organization-Id": "org_isolation_a"}

    async with get_client() as client:
        # User A accessing Org A -> 200 OK
        resp_a = await client.get("/v1/billing/invoices", headers=headers_a)
        assert resp_a.status_code == 200

        # User B trying to access Org A with Org A header -> 403 Forbidden
        resp_cross = await client.get("/v1/billing/invoices", headers=headers_b_fake_a)
        assert resp_cross.status_code == 403
        assert "Access to organization denied" in resp_cross.json()["detail"]


@pytest.mark.asyncio
async def test_api_key_hard_bounds_organization(get_client):
    raw_key, prefix, hashed_key = APIKeyService.generate_api_key()

    async with async_session_maker() as session:
        user_a = User(id="user_tenant_a", username="usera", email="a@test.com", password_hash="hash", is_admin=False)
        org_a = Organization(id="org_isolation_a", name="Org A", slug="org-a")
        role_admin = Role(id="admin", name="Admin", description="Admin Role")
        mem_a = Membership(user_id="user_tenant_a", organization_id="org_isolation_a", role_id="admin", status="active")

        for item in [role_admin, user_a, org_a, mem_a]:
            await session.merge(item)

        api_key_obj = APIKey(
            id="key_bound_1",
            user_id="user_tenant_a",
            organization_id="org_isolation_a",
            hashed_key=hashed_key,
            prefix=prefix,
            name="Test Key Org A",
        )
        await session.merge(api_key_obj)
        await session.commit()

    # Using API key enforces bound organization_id regardless of header
    headers = {"Authorization": f"Bearer {raw_key}"}
    async with get_client() as client:
        resp = await client.get("/v1/billing/invoices", headers=headers)
        assert resp.status_code == 200
