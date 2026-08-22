"""Integration tests for Orchestration REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_orchestration_rest_api_lifecycle():
    # 1. Health
    res_h = client.get("/v1/orchestration/health")
    assert res_h.status_code == 200

    # 2. Create Workflow
    res_wf = client.post("/v1/orchestration/workflows", json={
        "name": "API Test Workflow",
        "steps": [{"step_id": "s1", "name": "Step 1"}],
        "tenant_id": "t_api_orch",
    })
    assert res_wf.status_code == 201
    wf_id = res_wf.json()["workflow_id"]

    # 3. Publish Workflow
    res_pub = client.post(f"/v1/orchestration/workflows/{wf_id}/publish")
    assert res_pub.status_code == 200
    assert res_pub.json()["lifecycle_state"] == "PUBLISHED"

    # 4. Start Execution
    res_ex = client.post("/v1/orchestration/executions/start", json={
        "workflow_id": wf_id,
        "tenant_id": "t_api_orch",
        "inputs": {"test": 1},
    })
    assert res_ex.status_code == 200
    assert res_ex.json()["status"] == "RUNNING"

    # 5. Create Case
    res_case = client.post("/v1/orchestration/cases", json={
        "title": "Onboarding Case API",
        "case_type": "CUSTOMER_ONBOARDING",
        "tenant_id": "t_api_orch",
    })
    assert res_case.status_code == 201

    # 6. Analytics
    res_an = client.get("/v1/orchestration/analytics?tenant_id=t_api_orch")
    assert res_an.status_code == 200
    assert res_an.json()["automation_rate"] > 0
