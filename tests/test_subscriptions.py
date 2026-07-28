import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_plan_list(get_client, admin_token_headers):
    # Call the plans endpoint
    async with get_client() as client:
        response = await client.get("/v1/plans", headers=admin_token_headers)
        assert response.status_code == 200
        
        plans = response.json()
        assert isinstance(plans, list)

@pytest.mark.asyncio
async def test_get_subscription_not_found(get_client, admin_token_headers):
    # Org won't have a subscription initially
    async with get_client() as client:
        response = await client.get("/v1/subscriptions", headers=admin_token_headers)
        assert response.status_code == 404
        assert response.json()["detail"] == "No active subscription found"
