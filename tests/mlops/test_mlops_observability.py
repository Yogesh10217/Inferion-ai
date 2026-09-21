"""Unit tests for MLOpsMetricsCollector."""

from app.mlops.observability import MLOpsMetricsCollector


def test_metrics_collection():
    coll = MLOpsMetricsCollector()
    coll.record_event("ai_asset_versions_total", 3)
    coll.record_event("ai_deployments_total", 1)

    summary = coll.get_summary()
    assert summary["ai_asset_versions_total"] == 3
    assert summary["ai_deployments_total"] == 1
