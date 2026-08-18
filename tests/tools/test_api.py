"""
Tests for FastAPI Tool Endpoints (/v1/tools)
"""

import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.core.config import get_settings

# Create test app with auth_enabled = False for isolated tool API testing
settings = get_settings()
settings.auth_enabled = False
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

    # 2. Get tool details
    get_res = client.get("/v1/tools/custom_api_tool")
    assert get_res.status_code == 200
    assert get_res.json()["tool"]["name"] == "custom_api_tool"

    # 3. Execute tool with approval context
    exec_res = client.post(
        "/v1/tools/python_interpreter/execute",
        json={
            "parameters": {"code": "print('hello_api')"},
            "context": {"metadata": {"approval_status": "approved"}},
        },
    )
    assert exec_res.status_code == 200
    res_data = exec_res.json()["result"]
    assert res_data["status"] == "success"

    # 4. Audit & metrics
    audit_res = client.get("/v1/tools/python_interpreter/audit")
    assert audit_res.status_code == 200

    metrics_res = client.get("/v1/tools/python_interpreter/metrics")
    assert metrics_res.status_code == 200
