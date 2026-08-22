"""Unit tests for Webhooks HMAC SHA-256 signing and event engine."""

import pytest
from app.developer_platform.events import DeveloperEventEngine, DeveloperEvent


def test_webhook_signing_and_dispatch():
    engine = DeveloperEventEngine()

    sub = engine.create_subscription(
        developer_id="dev_web",
        target_url="https://example.com/webhook",
        event_types=["agent.completed"],
    )

    evt = DeveloperEvent(event_type="agent.completed", payload={"agent_id": "a1", "status": "COMPLETED"})
    deliveries = engine.dispatch_event(evt)

    assert len(deliveries) == 1
    assert deliveries[0].success is True
    assert len(deliveries[0].signature) == 64  # SHA-256 hex length
