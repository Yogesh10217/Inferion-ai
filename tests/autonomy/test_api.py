"""
Tests for Autonomy & Workers API Endpoints
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import create_app

settings = get_settings()


@pytest.fixture(autouse=True)
def disable_auth():
    original = settings.auth_enabled
    settings.auth_enabled = False
    yield
    settings.auth_enabled = original


test_app = create_app()
client = TestClient(test_app)


def test_autonomy_and_workers_api():
    # 1. Autonomy submit goal
    res_auto = client.post("/v1/autonomy/goals", json={"goal": "API test goal"})
    assert res_auto.status_code == 201

    # 2. List executions
    res_execs = client.get("/v1/autonomy/executions")
    assert res_execs.status_code == 200

    # 3. List workers
    res_workers = client.get("/v1/workers")
    assert res_workers.status_code == 200
