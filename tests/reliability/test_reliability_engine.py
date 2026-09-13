"""
Tests for Reliability Engineering Engine.
"""

from app.reliability.reliability_engine import ReliabilityEngineeringEngine, ReliabilityStatus


def test_reliability_score_boundaries():
    engine = ReliabilityEngineeringEngine()

    # 100% score
    res_100 = engine.evaluate_reliability()
    assert res_100.overall_score == 100.0
    assert res_100.status == ReliabilityStatus.HEALTHY

    # Low score
    res_low = engine.evaluate_reliability(
        application_resilience_score=20.0,
        database_resilience_score=20.0,
        cache_resilience_score=20.0,
        network_resilience_score=20.0,
        dependency_resilience_score=20.0,
        container_resilience_score=20.0,
        recovery_capability_score=20.0,
        failover_readiness_score=20.0,
        observability_detection_score=20.0,
        security_dependency_score=20.0,
    )
    assert res_low.overall_score == 20.0
    assert res_low.status == ReliabilityStatus.FAILING


def test_reliability_unexecuted_and_blocked():
    engine = ReliabilityEngineeringEngine()
    res_unex = engine.evaluate_reliability(executed=False)
    assert res_unex.status == ReliabilityStatus.NOT_EXECUTED

    res_block = engine.evaluate_reliability(blocked=True)
    assert res_block.status == ReliabilityStatus.BLOCKED
