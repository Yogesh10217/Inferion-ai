"""
Tests for FastAPI Team Endpoints (/v1/teams)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.config import get_settings

settings = get_settings()
settings.auth_enabled = False
test_app = create_app()

client = TestClient(test_app)


def test_teams_api_crud_and_run():
    # 1. List teams
    res_list = client.get("/v1/teams")
    assert res_list.status_code == 200
    assert "teams" in res_list.json()

    # 2. Create team
    res_create = client.post("/v1/teams", json={"name": "API Test Team", "team_type": "engineering"})
    assert res_create.status_code == 201
    tid = res_create.json()["team_id"]

    # 3. Get team
    res_get = client.get(f"/v1/teams/{tid}")
    assert res_get.status_code == 200
    assert res_get.json()["team_id"] == tid

    # 4. Run team
    res_run = client.post(f"/v1/teams/{tid}/run", json={"goal": "Test goal for team execution"})
    assert res_run.status_code == 200
    assert res_run.json()["result"]["status"] == "completed"

    # 5. Members / Messages / Metrics / Billing
    assert client.get(f"/v1/teams/{tid}/members").status_code == 200
    assert client.get(f"/v1/teams/{tid}/messages").status_code == 200
    assert client.get(f"/v1/teams/{tid}/metrics").status_code == 200
    assert client.get(f"/v1/teams/{tid}/billing").status_code == 200
