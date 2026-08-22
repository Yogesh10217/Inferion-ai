"""
Tests for Planning API Endpoints (/v1/plans)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.config import get_settings

settings = get_settings()


@pytest.fixture(autouse=True)
def disable_auth():
    original = settings.auth_enabled
    settings.auth_enabled = False
    yield
    settings.auth_enabled = original


test_app = create_app()
client = TestClient(test_app)


def test_plans_api_crud_and_simulate_execute():
    # 1. Create Plan
    res_create = client.post(
        "/v1/plans",
        json={"title": "API test plan goal", "description": "context"},
    )
    assert res_create.status_code == 201
    plan_data = res_create.json()["plan"]
    plan_id = plan_data["plan_id"]

    # 2. Get Plan
    res_get = client.get(f"/v1/plans/{plan_id}")
    assert res_get.status_code == 200
    assert res_get.json()["plan"]["title"] == "API test plan goal"

    # 3. Simulate Plan
    res_sim = client.post(f"/v1/plans/{plan_id}/simulate")
    assert res_sim.status_code == 200
    assert res_sim.json()["simulation"]["status"] == "simulated"

    # 4. Execute Plan
    res_exec = client.post(f"/v1/plans/{plan_id}/execute", json={"budget_dollars": 50.0})
    assert res_exec.status_code == 200
    assert res_exec.json()["status"] == "completed"
