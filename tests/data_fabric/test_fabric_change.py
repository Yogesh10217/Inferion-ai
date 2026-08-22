"""Unit tests for ChangeDetector."""

import pytest
from app.data_fabric.change_detection import ChangeDetector, ChangeType


def test_change_event_detection_and_listener_dispatch():
    detector = ChangeDetector()
    dispatched = []

    def listener(event):
        dispatched.append(event)

    detector.register_listener(listener)

    evt = detector.record_change(
        source_id="ds_cdc",
        change_type=ChangeType.UPDATED,
        record_id="rec_99",
        table_or_resource="users",
    )

    assert evt.change_type == ChangeType.UPDATED
    assert len(dispatched) == 1
    assert dispatched[0].event_id == evt.event_id
