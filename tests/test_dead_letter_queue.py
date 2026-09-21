from unittest.mock import AsyncMock, patch

import pytest

from app.core.database import async_session_maker
from app.events import (
    DeadLetterQueue,
    DeliveryService,
    EventEnvelope,
    EventStorage,
)


@pytest.mark.asyncio
async def test_dead_letter_queue_routing_and_replay():
    async with async_session_maker() as session:
        storage = EventStorage(session)
        delivery_svc = DeliveryService(storage, http_timeout=1.0)
        dlq = DeadLetterQueue(storage, delivery_svc)

        # Create endpoint pointing to unreachable port to force retry failure -> DLQ
        ep = await storage.create_endpoint(
            organization_id="org_dlq_test",
            url="http://127.0.0.1:59999/nonexistent",
            secret="dlq_secret",
            event_types=["budget.exceeded"],
            retry_policy={"max_retries": 2, "initial_interval_ms": 10, "jitter_ratio": 0.0},
        )

        envelope = EventEnvelope(
            event_type="budget.exceeded",
            payload={"organization_id": "org_dlq_test", "hard_limit": 500.0},
            organization_id="org_dlq_test",
        )

        await storage.persist_event(envelope)

        # Deliver to endpoint (will fail both retries)
        delivery = await delivery_svc.deliver_event_to_endpoint(ep, envelope)

        assert delivery.status == "failed"
        assert delivery.attempts == 2

        # Check DLQ record was created
        dl_records = await storage.list_dead_letters()
        assert len(dl_records) >= 1
        dl_item = [d for d in dl_records if d.delivery_id == delivery.id][0]
        assert dl_item.endpoint_id == ep.id
        assert dl_item.event_id == envelope.event_id

        # Test Replay with mock to simulate successful replay
        with patch.object(delivery_svc, "deliver_event_to_endpoint", new_callable=AsyncMock) as mock_deliver:
            mock_deliver.return_value = await storage.create_delivery(ep.id, envelope.event_id, is_replay=True)

            replayed_delivery = await dlq.replay_delivery(delivery.id)

            assert replayed_delivery.is_replay is True
            mock_deliver.assert_awaited_once()

            # Confirm original event & delivery history are untouched
            orig_event = await storage.get_event(envelope.event_id)
            assert orig_event is not None
            assert orig_event.id == envelope.event_id
