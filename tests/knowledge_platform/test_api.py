"""Integration tests for Knowledge Platform REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_knowledge_platform_api_lifecycle():
    # 1. Health
    res_h = client.get("/v1/knowledge_platform/health")
    assert res_h.status_code == 200

    # 2. Create Knowledge
    res_k = client.post("/v1/knowledge_platform/knowledge", json={
        "title": "API Spec Document",
        "content": "REST API definitions for Phase 5.19",
        "tenant_id": "t_api_kp",
    })
    assert res_k.status_code == 201
    item_id = res_k.json()["item_id"]

    # 3. Get Knowledge
    res_get = client.get(f"/v1/knowledge_platform/knowledge/{item_id}")
    assert res_get.status_code == 200
    assert res_get.json()["title"] == "API Spec Document"

    # 4. Retrieve Knowledge
    res_ret = client.post("/v1/knowledge_platform/retrieve", json={
        "query": "REST API",
        "tenant_id": "t_api_kp",
        "identity_id": "user_api",
        "user_role": "admin",
    })
    assert res_ret.status_code == 200

    # 5. Store Memory
    res_mem = client.post("/v1/knowledge_platform/memory", json={
        "key": "api_pref",
        "value": "json",
        "tenant_id": "t_api_kp",
    })
    assert res_mem.status_code == 201

    # 6. Analytics
    res_an = client.get("/v1/knowledge_platform/analytics?tenant_id=t_api_kp")
    assert res_an.status_code == 200
