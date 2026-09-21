import pytest


@pytest.mark.asyncio
async def test_list_users(get_client, admin_token_headers: dict):
    async with get_client() as client:
        response = await client.get("/v1/admin/users", headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


@pytest.mark.asyncio
async def test_list_organizations(get_client, admin_token_headers: dict):
    async with get_client() as client:
        response = await client.get("/v1/admin/organizations", headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "status" in data[0]


@pytest.mark.asyncio
async def test_suspend_organization(get_client, admin_token_headers: dict):
    async with get_client() as client:
        # First get an org
        response = await client.get("/v1/admin/organizations", headers=admin_token_headers)
        org_id = response.json()[0]["id"]

        # Suspend it
        payload = {"status": "suspended", "actor_id": "test_admin"}
        response = await client.patch(f"/v1/admin/organizations/{org_id}", json=payload, headers=admin_token_headers)
        assert response.status_code == 200
        assert response.json()["status"] == "suspended"


@pytest.mark.asyncio
async def test_non_admin_cannot_access_admin_routes(get_client, user1_token_headers: dict):
    async with get_client() as client:
        # user1_token_headers is for a normal user
        response = await client.get("/v1/admin/users", headers=user1_token_headers)
        assert response.status_code == 403
