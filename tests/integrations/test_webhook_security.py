"""Unit tests for Webhook pre-processing signature verification & duplicate protection."""

import pytest

from app.integrations.exceptions import DuplicateWebhookException, WebhookSignatureException
from app.integrations.webhooks import WebhookManager


def test_webhook_invalid_signature_and_duplicate_protection():
    wm = WebhookManager()
    ep = wm.create_endpoint(url="https://api.example.com/webhook", secret_token="sec_token", tenant_id="t_sec")

    # 1. Invalid signature header raises WebhookSignatureException BEFORE payload processing
    with pytest.raises(WebhookSignatureException):
        wm.process_inbound_webhook(
            endpoint_id=ep.endpoint_id, payload={"type": "event"}, signature_header="INVALID_SIGNATURE"
        )

    # 2. Duplicate event ID raises DuplicateWebhookException
    wm.process_inbound_webhook(
        endpoint_id=ep.endpoint_id, payload={"type": "event"}, signature_header="valid_sig", event_id="evt_dup_101"
    )
    with pytest.raises(DuplicateWebhookException):
        wm.process_inbound_webhook(
            endpoint_id=ep.endpoint_id, payload={"type": "event"}, signature_header="valid_sig", event_id="evt_dup_101"
        )
