"""Unit tests for ControlPlaneUsageAnalytics."""

from app.control_plane.usage_analytics import ControlPlaneUsageAnalytics
from app.control_plane.usage_manager import ControlPlaneUsageManager


def test_usage_and_cost_reporting():
    um = ControlPlaneUsageManager()
    analytics = ControlPlaneUsageAnalytics(usage_manager=um)

    um.record_event(tenant_id="t_report", requests=100, tokens=10000, cost_dollars=1.0)

    report = analytics.generate_tenant_report("t_report")
    assert report["summary"]["total_requests"] == 100
    assert report["summary"]["total_tokens"] == 10000

    cost_rep = analytics.generate_cost_breakdown("t_report")
    assert cost_rep["total_cost_dollars"] == 1.0
