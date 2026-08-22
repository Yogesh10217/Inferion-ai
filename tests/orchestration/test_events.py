"""Unit tests for EventRouter correlation and deduplication."""

import pytest
from app.orchestration.events import EventRouter


def test_event_dispatch_and_correlation():
    router = EventRouter()

    evt1 = router.dispatch_event("order_placed", {"order_id": "ord_100"}, tenant_id="t_evt")
    assert evt1.event_type == "order_placed"
    assert evt1.correlation_id is not None
