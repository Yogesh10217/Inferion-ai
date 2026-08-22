"""Integration tests for Control Plane REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_control_plane_summary_api():
    res = client.get("/v1/control-plane/summary")
    assert res.status_code == 200
    assert res.json()["status"] == "OPERATIONAL"


def test_tenant_and_org_api_flow():
    # Provision tenant
    res_t = client.post("/v1/control-plane/tenants", json={"name": "API Corp"})
    assert res_t.status_code == 201
    t_id = res_t.json()["tenant_bundle"]["tenant"]["tenant_id"]

    # List tenants
    res_list = client.get("/v1/control-plane/tenants")
    assert res_list.status_code == 200

    # Suspend tenant
    res_susp = client.post(f"/v1/control-plane/tenants/{t_id}/suspend")
    assert res_susp.status_code == 200
