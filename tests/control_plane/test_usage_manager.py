"""Unit tests for ControlPlaneUsageManager."""

from app.control_plane.usage_manager import ControlPlaneUsageManager


def test_usage_recording_and_aggregation():
    um = ControlPlaneUsageManager()

    um.record_event(tenant_id="tenant_um", requests=5, tokens=500, cost_dollars=0.05)
    um.record_event(tenant_id="tenant_um", requests=3, tokens=300, cost_dollars=0.03)

    rec = um.get_usage("tenant_um")
    assert rec.total_requests == 8
    assert rec.total_tokens == 800
    assert abs(rec.total_cost_dollars - 0.08) < 1e-5
