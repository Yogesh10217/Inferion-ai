"""Integration tests for Developer Platform REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_developer_registration_and_project_api():
    # Register developer
    res_dev = client.post("/v1/developers", json={
        "user_id": "usr_99",
        "full_name": "Alice Developer",
        "email": "alice@example.com",
    })
    assert res_dev.status_code == 201
    dev_id = res_dev.json()["developer"]["developer_id"]

    # Create project
    res_proj = client.post("/v1/developers/projects", json={
        "name": "Dev Project Alpha",
        "organization_id": "org_api",
        "workspace_id": "ws_api",
        "developer_id": dev_id,
    })
    assert res_proj.status_code == 201
    assert res_proj.json()["project"]["name"] == "Dev Project Alpha"

    # List projects
    res_list = client.get("/v1/developers/projects")
    assert res_list.status_code == 200
