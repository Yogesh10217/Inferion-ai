import pytest
from app.events import (
    DeadLetterQueue,
    DeliveryService,
    EventEnvelope,
    EventStorage,
    WebhookService,
)


@pytest.mark.asyncio
async def test_webhook_endpoint_crud(get_client, admin_token_headers):
    async with get_client() as client:
        # Create endpoint
        payload = {
            "organization_id": "test_org_id",
            "url": "https://example.com/webhook",
            "event_types": ["inference.completed", "user.created"],
            "secret": "test_webhook_secret_key",
        }
        res = await client.post("/v1/webhooks", json=payload, headers=admin_token_headers)
        assert res.status_code == 201
        data = res.json()
        endpoint_id = data["id"]
        assert data["url"] == "https://example.com/webhook"
        assert "inference.completed" in data["event_types"]

        # List endpoints
        res = await client.get("/v1/webhooks?organization_id=test_org_id", headers=admin_token_headers)
        assert res.status_code == 200
        endpoints = res.json()
        assert len(endpoints) >= 1

        # Update endpoint
        patch_payload = {"enabled": False}
        res = await client.patch(f"/v1/webhooks/{endpoint_id}", json=patch_payload, headers=admin_token_headers)
        assert res.status_code == 200
        assert res.json()["enabled"] is False

        # Delete endpoint
        res = await client.delete(f"/v1/webhooks/{endpoint_id}", headers=admin_token_headers)
        assert res.status_code == 200
        assert res.json()["status"] == "deleted"


@pytest.mark.asyncio
async def test_webhook_deliveries_and_events_api(get_client, admin_token_headers):
    async with get_client() as client:
        res = await client.get("/v1/webhooks/deliveries", headers=admin_token_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)

        res = await client.get("/v1/webhooks/events", headers=admin_token_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)
