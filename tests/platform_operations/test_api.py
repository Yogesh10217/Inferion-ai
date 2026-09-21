"""Unit tests for Platform Operations REST API endpoints."""

import pytest


@pytest.mark.asyncio
async def test_platform_operations_api_services_crud(get_client, admin_token_headers):
    async with get_client() as client:
        # Create service
        create_res = await client.post(
            "/v1/platform-operations/services",
            json={"name": "API Gateway Core", "tenant_id": "tenant_api", "service_tier": "TIER_0_CRITICAL"},
            headers=admin_token_headers,
        )
        assert create_res.status_code == 201
        svc = create_res.json()
        svc_id = svc["service_id"]

        # Get service
        get_res = await client.get(
            f"/v1/platform-operations/services/{svc_id}?tenant_id=tenant_api", headers=admin_token_headers
        )
        assert get_res.status_code == 200
        assert get_res.json()["name"] == "API Gateway Core"

        # List services
        list_res = await client.get(
            "/v1/platform-operations/services?tenant_id=tenant_api", headers=admin_token_headers
        )
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1


@pytest.mark.asyncio
async def test_platform_operations_api_signal_ingestion(get_client, admin_token_headers):
    async with get_client() as client:
        sig_res = await client.post(
            "/v1/platform-operations/signals",
            json={
                "source": "METRICS",
                "signal_type": "METRIC_THRESHOLD",
                "message": "High CPU utilization",
                "tenant_id": "tenant_api",
            },
            headers=admin_token_headers,
        )
        assert sig_res.status_code == 202
        assert sig_res.json()["signal_id"].startswith("sig_")
