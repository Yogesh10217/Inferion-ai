"""
Tests for Event Engine
"""

from app.autonomy.event_engine import AutonomyEvent, AutonomyEventType, EventEngine


def test_event_engine_subscribe_publish_replay():
    ee = EventEngine()
    received = []

    def on_workflow_completed(evt: AutonomyEvent):
        received.append(evt)

    ee.subscribe(AutonomyEventType.WORKFLOW_COMPLETED, on_workflow_completed)

    evt = AutonomyEvent(
        event_id="e1",
        event_type=AutonomyEventType.WORKFLOW_COMPLETED,
        source="unit_test",
        tenant_id="tenant_x",
    )
    ee.publish(evt)

    assert len(received) == 1
    assert received[0].event_id == "e1"

    history = ee.replay_events("tenant_x")
    assert len(history) == 1
