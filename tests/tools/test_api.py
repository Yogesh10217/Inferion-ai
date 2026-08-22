"""
Tests for FastAPI Tool Endpoints (/v1/tools)
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


def test_list_tools_api():
    response = client.get("/v1/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert len(data["tools"]) >= 1


def test_register_and_execute_tool_api():
    # 1. Register tool
    reg_res = client.post(
        "/v1/tools",
        json={
            "name": "custom_api_tool",
            "description": "Custom API tool",
            "category": "custom",
        },
    )
    assert reg_res.status_code == 201
    tool_name = reg_res.json()["tool"]["name"]

    # 2. Get tool
    get_res = client.get(f"/v1/tools/{tool_name}")
    assert get_res.status_code == 200
    assert get_res.json()["tool"]["name"] == "custom_api_tool"

    # 3. Execute tool
    exec_res = client.post(
        f"/v1/tools/{tool_name}/execute",
        json={"parameters": {"param": "value"}},
    )
    assert exec_res.status_code == 200
    assert "result" in exec_res.json()
