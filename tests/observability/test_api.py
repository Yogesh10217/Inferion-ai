"""FastAPI TestClient tests for Observability REST API endpoints."""

from fastapi.testclient import TestClient

from app.auth.jwt_service import JWTService
from app.main import app

client = TestClient(app)


def get_auth_headers(tenant_id: str = "tenant-test-api") -> dict:
    token = JWTService.create_access_token({"sub": "admin_user_id"})
    return {
        "Authorization": f"Bearer {token}",
        "X-Organization-Id": "test_org_id",
        "X-Tenant-Id": tenant_id,
    }


def test_api_get_traces():
    resp = client.get("/v1/observability/traces", headers=get_auth_headers("tenant-test-api"))
    assert resp.status_code == 200
    data = resp.json()
    assert "count" in data
    assert data["tenant_id"] == "tenant-test-api"


def test_api_get_costs():
    resp = client.get("/v1/observability/costs", headers=get_auth_headers())
    assert resp.status_code == 200


def test_api_get_performance():
    resp = client.get("/v1/observability/performance", headers=get_auth_headers())
    assert resp.status_code == 200


def test_api_get_anomalies():
    resp = client.get("/v1/observability/anomalies", headers=get_auth_headers())
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_api_get_alerts():
    resp = client.get("/v1/observability/alerts", headers=get_auth_headers())
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_api_operations_status_and_dashboard():
    resp_status = client.get("/v1/operations/status", headers=get_auth_headers())
    assert resp_status.status_code == 200
    assert "status" in resp_status.json()

    resp_dash = client.get("/v1/operations/dashboard", headers=get_auth_headers())
    assert resp_dash.status_code == 200
    assert "performance_by_component" in resp_dash.json()
