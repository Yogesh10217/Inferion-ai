"""Tests for SLAEngine and SLOStatus evaluation."""

from app.observability.sla import SLAEngine, SLOStatus


def test_slo_evaluation():
    engine = SLAEngine()
    engine.create_slo(
        slo_id="slo-latency",
        name="P95 Latency SLO",
        target_component="gateway",
        metric_name="latency_p95",
        comparator="<=",
        target_value=2000.0,
        warning_threshold=1500.0,
    )

    # Healthy check
    res1 = engine.evaluate_slo("slo-latency", current_value=1200.0)
    assert res1.status == SLOStatus.HEALTHY
    assert res1.is_violated is False

    # Warning check
    res2 = engine.evaluate_slo("slo-latency", current_value=1600.0)
    assert res2.status == SLOStatus.WARNING
    assert res2.is_violated is False

    # Violation check
    res3 = engine.evaluate_slo("slo-latency", current_value=2500.0)
    assert res3.status == SLOStatus.VIOLATED
    assert res3.is_violated is True
