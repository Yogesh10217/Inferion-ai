"""Unit tests for OrchestrationMetricsCollector."""

from app.orchestration.observability import OrchestrationMetricsCollector


def test_orchestration_metrics():
    collector = OrchestrationMetricsCollector()
    collector.record_execution("t_obs", "COMPLETED")
    collector.record_human_task("t_obs", "ASSIGNED")
