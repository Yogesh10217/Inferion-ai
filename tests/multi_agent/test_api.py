"""
Tests for Multi-Agent Teams API Endpoints (/v1/teams)
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


def test_teams_api_crud_and_run():
    # 1. Create Team
    res_create = client.post(
        "/v1/teams",
        json={
            "name": "API Research Team",
            "pattern": "hierarchical",
            "agent_ids": ["researcher", "writer"],
        },
    )
    assert res_create.status_code == 201
    team_data = res_create.json()
    team_id = team_data["team_id"]

    # 2. List Teams
    res_list = client.get("/v1/teams")
    assert res_list.status_code == 200
    assert "teams" in res_list.json()

    # 3. Get Team
    res_get = client.get(f"/v1/teams/{team_id}")
    assert res_get.status_code == 200
    assert res_get.json()["name"] == "API Research Team"

    # 4. Run Team Task
    res_run = client.post(
        f"/v1/teams/{team_id}/run",
        json={"goal": "API multi-agent research task"},
    )

    assert res_run.status_code == 200
    assert "result" in res_run.json()
