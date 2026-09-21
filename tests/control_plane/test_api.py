"""Integration tests for Control Plane REST API endpoints."""

from fastapi.testclient import TestClient

from app.auth.jwt_service import JWTService
from app.main import app

client = TestClient(app)


def get_auth_headers() -> dict:
    token = JWTService.create_access_token({"sub": "admin_user_id"})
    return {
        "Authorization": f"Bearer {token}",
        "X-Organization-Id": "test_org_id",
    }


def test_control_plane_summary_api():
    res = client.get("/v1/control-plane/summary", headers=get_auth_headers())
    assert res.status_code == 200
    assert res.json()["status"] == "OPERATIONAL"


def test_tenant_and_org_api_flow():
    # Provision tenant
    res_t = client.post("/v1/control-plane/tenants", json={"name": "API Corp"}, headers=get_auth_headers())
    assert res_t.status_code == 201
    t_id = res_t.json()["tenant_bundle"]["tenant"]["tenant_id"]

    # List tenants
    res_list = client.get("/v1/control-plane/tenants", headers=get_auth_headers())
    assert res_list.status_code == 200

    # Suspend tenant
    res_susp = client.post(f"/v1/control-plane/tenants/{t_id}/suspend", headers=get_auth_headers())
    assert res_susp.status_code == 200
