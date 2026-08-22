"""FastAPI TestClient tests for Observability REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_get_traces():
    resp = client.get("/v1/observability/traces", headers={"X-Tenant-Id": "tenant-test-api"})
    assert resp.status_code == 200
    data = resp.json()
    assert "count" in data
    assert data["tenant_id"] == "tenant-test-api"


def test_api_get_costs():
    resp = client.get("/v1/observability/costs")
    assert resp.status_code == 200


def test_api_get_performance():
    resp = client.get("/v1/observability/performance")
    assert resp.status_code == 200


def test_api_get_anomalies():
    resp = client.get("/v1/observability/anomalies")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_api_get_alerts():
    resp = client.get("/v1/observability/alerts")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_api_operations_status_and_dashboard():
    resp_status = client.get("/v1/operations/status")
    assert resp_status.status_code == 200
    assert "status" in resp_status.json()

    resp_dash = client.get("/v1/operations/dashboard")
    assert resp_dash.status_code == 200
    assert "performance_by_component" in resp_dash.json()
