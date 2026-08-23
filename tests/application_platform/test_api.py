"""Unit tests for Application Platform REST API endpoints using FastAPI AsyncClient."""

import pytest


@pytest.mark.asyncio
async def test_api_health_endpoint(get_client, admin_token_headers):
    async with get_client() as client:
        response = await client.get("/v1/applications/health", headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "OPERATIONAL"


@pytest.mark.asyncio
async def test_api_application_crud(get_client, admin_token_headers):
    async with get_client() as client:
        create_res = await client.post(
            "/v1/applications",
            json={"name": "API Support App", "app_type": "COPILOT", "tenant_id": "tenant_api"},
            headers=admin_token_headers,
        )
        assert create_res.status_code == 201
        created_app = create_res.json()
        app_id = created_app["application_id"]

        get_res = await client.get(f"/v1/applications/{app_id}?tenant_id=tenant_api", headers=admin_token_headers)
        assert get_res.status_code == 200
        assert get_res.json()["name"] == "API Support App"

        list_res = await client.get("/v1/applications?tenant_id=tenant_api", headers=admin_token_headers)
        assert list_res.status_code == 200
        assert len(list_res.json()) >= 1
