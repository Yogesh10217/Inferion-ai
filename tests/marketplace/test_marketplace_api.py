"""Integration tests for Marketplace REST API endpoints."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_marketplace_item_lifecycle_api():
    manifest = {
        "identifier": "api.mkt.ext",
        "name": "API Ext",
        "publisher_id": "pub_api",
        "extension_type": "TOOL",
    }

    # 1. Create item
    res_c = client.post(
        "/v1/marketplace/items",
        json={
            "title": "API Extension",
            "summary": "Extension via REST",
            "category": "TOOLS",
            "publisher_id": "pub_api",
            "manifest": manifest,
        },
    )
    assert res_c.status_code == 201
    item_id = res_c.json()["item"]["item_id"]

    # 2. Submit
    res_sub = client.post(f"/v1/marketplace/items/{item_id}/submit")
    assert res_sub.status_code == 200

    # 3. Publish
    res_pub = client.post(f"/v1/marketplace/items/{item_id}/publish")
    assert res_pub.status_code == 200

    # 4. Install
    res_inst = client.post(f"/v1/marketplace/items/{item_id}/install", json={"tenant_id": "t_api"})
    assert res_inst.status_code == 200
    assert res_inst.json()["extension"]["tenant_id"] == "t_api"
