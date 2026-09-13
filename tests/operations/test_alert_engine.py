from app.operations.alerting import Alert, AlertEngine, AlertSeverity, AlertStatus


def test_alert_engine_generation():
    engine = AlertEngine()
    alerts = engine.generate_alerts(
        slo_results=[],
        error_budget_result=None,
        anomalies=[],
    )
    assert len(alerts) == 0
