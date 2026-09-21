"""Unit tests for ControlPlaneMetricsCollector."""

from app.control_plane.control_plane_metrics import ControlPlaneMetricsCollector


def test_control_plane_metrics_collection():
    coll = ControlPlaneMetricsCollector()
    coll.increment("control_plane_requests_total", 5.0)
    coll.increment("tenants_total", 2.0)

    summary = coll.get_metrics_summary()
    assert summary["control_plane_requests_total"] == 5.0
    assert summary["tenants_total"] == 2.0
