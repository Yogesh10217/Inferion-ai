import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_system_stats(get_client, admin_token_headers: dict):
    async with get_client() as client:
        response = await client.get("/v1/admin/system", headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert "organizations" in data
        assert "active" in data["organizations"]
        assert "users" in data

@pytest.mark.asyncio
async def test_health_stats(get_client, admin_token_headers: dict):
    async with get_client() as client:
        response = await client.get("/v1/admin/health", headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert "application" in data
        assert "version" in data["application"]
        assert "database" in data
        assert "status" in data["database"]
