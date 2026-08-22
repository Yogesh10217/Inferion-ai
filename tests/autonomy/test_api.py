"""
Tests for Autonomy & Workers API Endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.config import get_settings

settings = get_settings()
settings.auth_enabled = False
test_app = create_app()

client = TestClient(test_app)


def test_autonomy_and_workers_api():
    # 1. Autonomy submit goal
    res_auto = client.post("/v1/autonomy/goals", json={"goal": "API test goal"})
    assert res_auto.status_code == 201

    # 2. List executions
    res_execs = client.get("/v1/autonomy/executions")
    assert res_execs.status_code == 200

    # 3. Create worker
    res_wrk = client.post("/v1/workers", json={"name": "API Worker", "template_type": "support"})
    assert res_wrk.status_code == 201
    wid = res_wrk.json()["worker"]["worker_id"]

    # 4. Assign goal to worker
    res_wgoal = client.post(f"/v1/workers/{wid}/goal", json={"goal": "Support ticket resolution"})
    assert res_wgoal.status_code == 200

    # 5. Delete worker
    assert client.delete(f"/v1/workers/{wid}").status_code == 200
