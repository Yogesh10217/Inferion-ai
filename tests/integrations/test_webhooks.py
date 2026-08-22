"""Unit tests for WebhookManager and delivery processing."""

import pytest
from app.integrations.webhooks import WebhookManager


def test_webhook_endpoint_creation_and_delivery():
    wm = WebhookManager()
    ep = wm.create_endpoint(url="https://api.example.com/webhook", secret_token="token_123", tenant_id="t_wh")

    deliv = wm.process_inbound_webhook(endpoint_id=ep.endpoint_id, payload={"type": "event"}, signature_header="valid_sig")
    assert deliv.status == "DELIVERED"
