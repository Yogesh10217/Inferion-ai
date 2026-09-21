"""Unit tests for Intelligence REST API Endpoints."""

import pytest


@pytest.mark.asyncio
async def test_intelligence_api_signal_ingest(get_client, admin_token_headers):
    async with get_client() as client:
        res = await client.post(
            "/v1/intelligence/signals",
            json={
                "source": "OPERATIONS",
                "signal_type": "METRIC_THRESHOLD",
                "message": "High CPU utilization",
                "tenant_id": "tenant_api",
            },
            headers=admin_token_headers,
        )
        assert res.status_code == 202
        assert res.json()["signal_id"].startswith("sig_")


@pytest.mark.asyncio
async def test_intelligence_api_forecast(get_client, admin_token_headers):
    async with get_client() as client:
        res = await client.post(
            "/v1/intelligence/forecast",
            json={
                "target_resource_id": "res_svc_api",
                "forecast_type": "INCIDENT_RISK_FORECAST",
                "tenant_id": "tenant_api",
            },
            headers=admin_token_headers,
        )
        assert res.status_code == 200
        assert res.json()["forecast_id"].startswith("fc_")
