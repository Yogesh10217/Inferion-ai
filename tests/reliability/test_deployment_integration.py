"""
Tests for Integration with Phase 5.67 Deployment Execution.
"""

from app.deployment.rollback import RollbackStrategyEngine
from app.reliability.recovery_recommendation import RecoveryAction, RecoveryRecommendationEngine


def test_deployment_integration_rollback_recommendation_non_destructive():
    engine = RecoveryRecommendationEngine()
    rec = engine.generate_recommendation(deployment_failed=True)
    assert rec.action == RecoveryAction.ROLLBACK_RECOMMENDED
    assert rec.auto_execution_blocked is True
