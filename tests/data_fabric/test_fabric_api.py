"""Integration tests for Data Fabric REST API endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_data_fabric_rest_api_lifecycle():
    # 1. Create data source
    res_c = client.post("/v1/data-sources", json={
        "name": "API Postgres Source",
        "source_type": "POSTGRES",
        "connector_type": "POSTGRES",
        "tenant_id": "t_api_df",
    })
    assert res_c.status_code == 201
    ds_id = res_c.json()["data_source"]["id"]

    # 2. List data sources
    res_l = client.get("/v1/data-sources", params={"tenant_id": "t_api_df"})
    assert res_l.status_code == 200
    assert len(res_l.json()["data_sources"]) == 1

    # 3. Discover schema
    res_sch = client.post(f"/v1/data-sources/{ds_id}/discover")
    assert res_sch.status_code == 200

    # 4. Trigger sync
    res_sync = client.post(f"/v1/data-sources/{ds_id}/sync", json={"strategy": "FULL"})
    assert res_sync.status_code == 200
    assert res_sync.json()["sync_job"]["status"] == "COMPLETED"

    # 5. Governance access check
    res_gov = client.post("/v1/data-governance/access-check", json={
        "resource_id": ds_id,
        "tenant_id": "t_api_df",
        "classification": "INTERNAL",
        "requester_id": "usr_test",
    })
    assert res_gov.status_code == 200
    assert res_gov.json()["decision"]["permitted"] is True
