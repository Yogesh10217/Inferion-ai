"""
Tests for Workflow REST API Router Endpoints (/v1/workflows)
"""

import pytest


@pytest.mark.asyncio
async def test_create_and_list_workflows_api(get_client, admin_token_headers):
    req_payload = {
        "name": "Test API Workflow",
        "description": "Integration testing for REST API",
        "spec": {
            "nodes": [{"id": "a1", "type": "AGENT", "agent_id": "test_agent"}],
            "edges": [{"source": "START", "target": "a1"}, {"source": "a1", "target": "END"}],
        },
    }

    async with get_client() as async_client:
        response = await async_client.post("/v1/workflows", json=req_payload, headers=admin_token_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        wf_id = data["workflow"]["id"]

        # List
        list_res = await async_client.get("/v1/workflows", headers=admin_token_headers)
        assert list_res.status_code == 200
        wfs = list_res.json()
        assert any(wf["id"] == wf_id for wf in wfs)

        # Get single
        get_res = await async_client.get(f"/v1/workflows/{wf_id}", headers=admin_token_headers)
        assert get_res.status_code == 200
        assert get_res.json()["workflow"]["id"] == wf_id


@pytest.mark.asyncio
async def test_run_workflow_api(get_client, admin_token_headers):
    req_payload = {
        "name": "API Execution Workflow",
        "spec": {
            "nodes": [{"id": "a1", "type": "AGENT", "agent_id": "agent_x"}],
            "edges": [{"source": "START", "target": "a1"}, {"source": "a1", "target": "END"}],
        },
    }

    async with get_client() as async_client:
        create_res = await async_client.post("/v1/workflows", json=req_payload, headers=admin_token_headers)
        wf_id = create_res.json()["workflow"]["id"]

        run_res = await async_client.post(
            f"/v1/workflows/{wf_id}/run", json={"inputs": {"q": "hello"}}, headers=admin_token_headers
        )
        assert run_res.status_code == 200
        exec_data = run_res.json()["execution"]
        assert exec_data["status"] == "COMPLETED"
        assert "run_id" in exec_data


@pytest.mark.asyncio
async def test_list_templates_api(get_client, admin_token_headers):
    async with get_client() as async_client:
        res = await async_client.get("/v1/workflows/templates", headers=admin_token_headers)
        assert res.status_code == 200
        templates = res.json()
        assert len(templates) >= 10
