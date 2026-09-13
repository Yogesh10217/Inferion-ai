from app.operations.observability_engine import ObservabilityEngine, ObservationStatus


def test_observability_engine_healthy():
    engine = ObservabilityEngine()
    res = engine.collect_observations(
        app_data={"request_count": 1000, "failure_count": 0, "latency_p95": 120.0},
        health_data={"live": True, "ready": True, "health": True},
    )
    assert res.status == ObservationStatus.HEALTHY
    assert res.application_metrics["availability"] == 1.0
    assert len(res.observations) == 3


def test_observability_engine_degraded():
    engine = ObservabilityEngine()
    res = engine.collect_observations(
        app_data={"request_count": 1000, "failure_count": 80, "error_rate": 0.08, "latency_p95": 600.0},
    )
    assert res.status == ObservationStatus.DEGRADED
