"""Integration tests for MLOps REST API endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_mlops_rest_api_lifecycle():
    # 1. Create asset
    res_c = client.post(
        "/v1/mlops/assets",
        json={
            "name": "API Agent Asset",
            "asset_type": "AGENT",
            "tenant_id": "t_api_mlops",
            "description": "Agent for REST testing",
        },
    )
    assert res_c.status_code == 201
    asset_id = res_c.json()["asset"]["asset_id"]

    # 2. List assets
    res_l = client.get("/v1/mlops/assets", params={"tenant_id": "t_api_mlops"})
    assert res_l.status_code == 200
    assert len(res_l.json()["assets"]) == 1

    # 3. Create version
    res_v = client.post(
        f"/v1/mlops/assets/{asset_id}/versions",
        json={
            "version_number": "1.1.0",
            "configuration": {"model": "gpt-4"},
            "changelog": "v1.1.0 update",
        },
    )
    assert res_v.status_code == 201

    # 4. Create deployment
    res_d = client.post(
        "/v1/mlops/deployments",
        json={
            "name": "API Dev Deployment",
            "asset_id": asset_id,
            "version_number": "1.1.0",
            "environment": "DEVELOPMENT",
            "tenant_id": "t_api_mlops",
        },
    )
    assert res_d.status_code == 201
    dep_id = res_d.json()["deployment"]["deployment_id"]

    # 5. Execute deployment
    res_dep = client.post(f"/v1/mlops/deployments/{dep_id}/deploy")
    assert res_dep.status_code == 200
    assert res_dep.json()["deployment"]["status"] == "ACTIVE"
