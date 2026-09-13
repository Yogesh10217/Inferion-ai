import pytest
from app.deployment.models import TrafficValidationStatus
from app.deployment.traffic_validation import TrafficValidationEngine


def test_traffic_validation_success_path():
    metrics = {
        "error_rate": 0.001,
        "p95_latency_ms": 150.0,
        "success_rate": 0.999,
        "probes_healthy": True,
    }
    res = TrafficValidationEngine.validate_traffic(
        traffic_percentage=10,
        runtime_metrics=metrics,
        expected_artifact_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
        runtime_artifact_digest="sha256:1111222233334444555566667777888899990000aaaabbbbccccddddeeeeffff",
    )

    assert res.valid is True
    assert res.status == TrafficValidationStatus.PASSED
    assert len(res.blocking_reasons) == 0


def test_traffic_validation_error_rate_exceeded():
    metrics = {
        "error_rate": 0.05,  # 5% error rate (exceeds 1%)
        "p95_latency_ms": 150.0,
        "success_rate": 0.95,
        "probes_healthy": True,
    }
    res = TrafficValidationEngine.validate_traffic(
        traffic_percentage=10,
        runtime_metrics=metrics,
    )

    assert res.valid is False
    assert res.status == TrafficValidationStatus.FAILED
    assert any("exceeded threshold" in err for err in res.blocking_reasons)
