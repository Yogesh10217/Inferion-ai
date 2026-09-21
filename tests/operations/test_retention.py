"""Unit tests for TelemetryRetentionManager."""

from app.operations.storage import TelemetryRetentionManager


def test_telemetry_retention_policy():
    mgr = TelemetryRetentionManager()
    pol = mgr.set_policy("t_ret", hot_days=14, warm_days=60, archive_days=730)

    assert pol.hot_days == 14
    assert pol.archive_days == 730
