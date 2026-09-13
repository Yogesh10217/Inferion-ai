"""
Tests for Recovery Recommendation Module.
"""

from app.reliability.recovery_recommendation import RecoveryAction, RecoveryRecommendationEngine


def test_recovery_recommendation_safety():
    engine = RecoveryRecommendationEngine()

    # Failover recommendation auto execution blocked
    rec_failover = engine.generate_recommendation(primary_region_failed=True)
    assert rec_failover.action == RecoveryAction.FAILOVER_RECOMMENDED
    assert rec_failover.auto_execution_blocked is True

    # Restore recommendation auto execution blocked
    rec_restore = engine.generate_recommendation(database_failed=True)
    assert rec_restore.action == RecoveryAction.RESTORE_RECOMMENDED
    assert rec_restore.auto_execution_blocked is True
