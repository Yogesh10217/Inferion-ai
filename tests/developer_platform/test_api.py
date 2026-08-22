"""Unit tests for Developer Platform REST API router."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_health_and_project_creation():
    res_health = client.get("/v1/developer-platform/health")
    assert res_health.status_code == 200
    assert res_health.json()["subsystem"] == "DeveloperPlatformManager"

    res_proj = client.post(
        "/v1/developer-platform/projects",
        json={"name": "API Test Project", "tenant_id": "t_api_dev"},
    )
    assert res_proj.status_code == 201
    assert res_proj.json()["name"] == "API Test Project"
