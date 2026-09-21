"""Unit tests for Integration Platform REST API router."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_api_health_and_registration():
    res_health = client.get("/v1/integrations/health")
    assert res_health.status_code == 200
    assert res_health.json()["subsystem"] == "IntegrationManager"

    res_reg = client.post(
        "/v1/integrations",
        json={"name": "Test Integration", "category": "SAAS", "tenant_id": "t_api"},
    )
    assert res_reg.status_code == 201
    assert res_reg.json()["name"] == "Test Integration"
