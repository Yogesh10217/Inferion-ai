import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_search_audit_events_empty(get_client, admin_token_headers: dict):
    async with get_client() as client:
        response = await client.get("/v1/admin/audit?limit=10", headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
