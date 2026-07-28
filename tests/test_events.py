import pytest
from app.events import (
    EventEnvelope,
    EventPublisher,
    EventRegistry,
    InMemoryEventBus,
)


@pytest.mark.asyncio
async def test_event_bus_and_publisher_flow():
    bus = InMemoryEventBus()
    publisher = EventPublisher(event_bus=bus)

    received_events = []

    async def sample_handler(envelope: EventEnvelope):
        received_events.append(envelope)

    # Subscribe to specific event type
    bus.subscribe("inference.completed", sample_handler)

    # Publish event
    env = await publisher.publish(
        event_type="inference.completed",
        payload={"model": "gpt-4o", "tokens": 150},
        organization_id="org_test_123",
        actor="user_1",
    )

    assert env.event_type == "inference.completed"
    assert env.version == "1.0"
    assert env.organization_id == "org_test_123"
    assert len(received_events) == 1
    assert received_events[0].event_id == env.event_id


@pytest.mark.asyncio
async def test_subscriber_isolation():
    bus = InMemoryEventBus()

    failed_called = False
    success_called = False

    async def failing_handler(envelope: EventEnvelope):
        nonlocal failed_called
        failed_called = True
        raise RuntimeError("Subscriber crashed!")

    async def successful_handler(envelope: EventEnvelope):
        nonlocal success_called
        success_called = True

    bus.subscribe("user.created", failing_handler)
    bus.subscribe("user.created", successful_handler)

    publisher = EventPublisher(event_bus=bus)
    await publisher.publish(event_type="user.created", payload={"username": "alice"})

    # Even though failing_handler raised RuntimeError, subscriber isolation ensured successful_handler executed!
    assert failed_called is True
    assert success_called is True


def test_event_registry_metadata():
    assert EventRegistry.is_valid_event("organization.created") is True
    event_def = EventRegistry.get_event("organization.created")
    assert event_def is not None
    assert event_def.category == "tenant"
    assert event_def.version == "1.0"
    assert "provisioned" in event_def.description.lower()
