"""Tests for PerformanceMonitor and percentile calculations."""

import pytest
from app.observability.performance import PerformanceMonitor


def test_percentile_calculation():
    pm = PerformanceMonitor()
    latencies = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]

    stats = pm.calculate_percentiles(latencies)
    assert stats["min"] == 10.0
    assert stats["max"] == 100.0
    assert stats["avg"] == 55.0
    assert stats["p50"] > 0
    assert stats["p95"] > 0
    assert stats["p99"] > 0


def test_component_performance_tracking():
    pm = PerformanceMonitor()
    pm.record_latency("agent.execute", 100.0)
    pm.record_latency("agent.execute", 200.0, is_error=True)
    pm.record_latency("agent.execute", 150.0)

    summary = pm.get_component_performance("agent.execute")
    assert summary.count == 3
    assert summary.error_rate == pytest.approx(0.3333, abs=0.01)
    assert summary.avg_ms == 150.0
