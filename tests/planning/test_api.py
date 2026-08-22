"""
Tests for FastAPI Planning Endpoints (/v1/plans)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.config import get_settings

settings = get_settings()
settings.auth_enabled = False
test_app = create_app()

client = TestClient(test_app)


def test_plans_api_crud_and_simulate_execute():
    # 1. Create plan
    res_create = client.post("/v1/plans", json={"title": "API Test Plan", "description": "Testing plans endpoint"})
    assert res_create.status_code == 201
    pid = res_create.json()["plan"]["plan_id"]

    # 2. Get plan
    res_get = client.get(f"/v1/plans/{pid}")
    assert res_get.status_code == 200
    assert res_get.json()["plan"]["title"] == "API Test Plan"

    # 3. Simulate plan
    res_sim = client.post(f"/v1/plans/{pid}/simulate")
    assert res_sim.status_code == 200
    assert "expected_cost" in res_sim.json()["simulation"]

    # 4. Execute plan
    res_exec = client.post(f"/v1/plans/{pid}/execute", json={"budget_dollars": 50.0})
    assert res_exec.status_code == 200
    assert res_exec.json()["status"] == "completed"

    # 5. Reflect / Optimize / Metrics / Billing / History
    assert client.post(f"/v1/plans/{pid}/reflect").status_code == 200
    assert client.post(f"/v1/plans/{pid}/optimize").status_code == 200
    assert client.get(f"/v1/plans/{pid}/metrics").status_code == 200
    assert client.get(f"/v1/plans/{pid}/billing").status_code == 200
    assert client.get(f"/v1/plans/{pid}/history").status_code == 200
