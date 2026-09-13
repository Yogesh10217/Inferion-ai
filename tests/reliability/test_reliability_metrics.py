"""
Tests for Reliability Metrics Calculator Module.
"""

from app.reliability.reliability_metrics import ReliabilityMetricsCalculator


def test_reliability_metrics_calculations():
    calc = ReliabilityMetricsCalculator()
    res = calc.calculate_metrics(
        total_uptime_seconds=86300.0,
        total_downtime_seconds=100.0,
        successful_recoveries=9,
        failed_recoveries=1,
    )
    assert res.availability_percentage > 99.0
    assert res.recovery_success_rate == 90.0
    assert res.mean_time_to_detect_seconds > 0.0
    assert res.mean_time_to_recover_seconds > 0.0
