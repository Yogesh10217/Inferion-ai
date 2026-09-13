from app.operations.alerting import Alert, AlertSeverity, AlertStatus
from app.operations.recovery_decision import RecoveryDecisionEngine, RecoveryRecommendation


def test_recovery_decision_rollback_not_auto_executed():
    engine = RecoveryDecisionEngine()
    alerts = [
        Alert(
            alert_id="a-reg",
            source="DEPLOYMENT",
            alert_type="DEPLOYMENT_REGRESSION",
            service="enterprise-ai-platform",
            severity=AlertSeverity.CRITICAL,
            status=AlertStatus.OPEN,
            summary="Deployment regression",
            timestamp="2026-09-13T09:00:00Z",
            deployment_identity="dep-001",
        )
    ]

    dec = engine.evaluate_recovery(
        incident=None,
        slo_results=[],
        error_budget_result=None,
        alerts=alerts,
    )

    assert dec.recommendation == RecoveryRecommendation.ROLLBACK_RECOMMENDED
    assert dec.auto_execution_blocked is True
    # Verify strict safety contract: ROLLBACK_RECOMMENDED is not execution
    assert dec.recommendation != "PRODUCTION_ROLLBACK_EXECUTED"
