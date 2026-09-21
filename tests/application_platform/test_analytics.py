"""Unit tests for Application Analytics Engine."""

from app.application_platform.analytics import ApplicationAnalyticsEngine


def test_tenant_scoped_analytics_reporting():
    engine = ApplicationAnalyticsEngine()

    engine.record_metric("tenant_a", "app_1", "execution_count", 1.0)
    engine.record_metric("tenant_a", "app_1", "cost_usd", 0.02)
    engine.record_metric("tenant_a", "app_1", "latency_ms", 150.0)

    engine.record_metric("tenant_b", "app_1", "execution_count", 1.0)

    report_a = engine.generate_report("tenant_a", "app_1")
    assert report_a.total_executions == 1
    assert report_a.total_cost_usd == 0.02
    assert report_a.avg_latency_ms == 150.0

    report_b = engine.generate_report("tenant_b", "app_1")
    assert report_b.total_executions == 1
    assert report_b.total_cost_usd == 0.0
