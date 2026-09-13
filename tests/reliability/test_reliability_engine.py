"""
Tests for Reliability Engineering Engine.
"""

from app.reliability.reliability_engine import ReliabilityEngineeringEngine, ReliabilityStatus


def test_reliability_score_boundaries():
    engine = ReliabilityEngineeringEngine()

    # 100% score
    res_100 = engine.evaluate_reliability()
    assert res_100.overall_score == 100.0
    assert res_100.status == ReliabilityStatus.RELIABLE

    # Low score
    res_low = engine.evaluate_reliability(
        availability_score=20.0,
        redundancy_score=20.0,
        dependency_resilience_score=20.0,
        recovery_readiness_score=20.0,
        failure_detection_score=20.0,
        incident_response_score=20.0,
        rollback_readiness_score=20.0,
        backup_readiness_score=20.0,
        disaster_recovery_score=20.0,
        business_continuity_score=20.0,
    )
    assert res_low.overall_score == 20.0
    assert res_low.status == ReliabilityStatus.CRITICAL


def test_reliability_unexecuted_and_blocked():
    engine = ReliabilityEngineeringEngine()
    res_unex = engine.evaluate_reliability(executed=False)
    assert res_unex.status == ReliabilityStatus.NOT_EXECUTED

    res_block = engine.evaluate_reliability(blocked=True)
    assert res_block.status == ReliabilityStatus.BLOCKED
