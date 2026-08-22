"""Integration tests for Operations REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_operations_rest_api_lifecycle():
    # 1. Health
    res_h = client.get("/v1/operations/health")
    assert res_h.status_code == 200

    # 2. Topology
    res_top = client.get("/v1/operations/topology")
    assert res_top.status_code == 200

    # 3. Create SLO
    res_slo = client.post("/v1/operations/slos", json={
        "name": "API Latency SLO",
        "target_percentage": 99.5,
        "tenant_id": "t_api_ops",
        "slo_type": "LATENCY",
    })
    assert res_slo.status_code == 201

    # 4. List SLOs
    res_slos = client.get("/v1/operations/slos", params={"tenant_id": "t_api_ops"})
    assert res_slos.status_code == 200
    assert len(res_slos.json()["slos"]) == 1

    # 5. List alerts
    res_alt = client.get("/v1/operations/alerts")
    assert res_alt.status_code == 200

    # 6. Analytics
    res_an = client.get("/v1/operations/analytics")
    assert res_an.status_code == 200
