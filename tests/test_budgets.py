import pytest


@pytest.mark.asyncio
async def test_set_and_get_budget(get_client, admin_token_headers):
    # Set a budget
    payload = {
        "organization_id": "test_org_id",  # Assuming admin_token_headers uses test_org_id
        "hard_limit": 500.0,
        "warning_threshold": 400.0,
        "critical_threshold": 450.0,
        "enabled": True,
    }

    async with get_client() as client:
        response = await client.post("/v1/budgets", json=payload, headers=admin_token_headers)
        assert response.status_code == 200

        budget = response.json()
        assert budget["hard_limit"] == 500.0

        # Get budget
        response2 = await client.get("/v1/budgets", headers=admin_token_headers)
        assert response2.status_code == 200
        budgets = response2.json()
        assert len(budgets) >= 1
        assert budgets[0]["hard_limit"] == 500.0
