from app.operations.alerting import Alert, AlertSeverity, AlertStatus
from app.operations.incident_detection import IncidentDetectionEngine
from app.operations.incident_management import IncidentSeverity


def test_incident_detection_p1():
    engine = IncidentDetectionEngine()
    alerts = [
        Alert(
            alert_id="a1",
            source="ERROR_BUDGET",
            alert_type="ERROR_BUDGET_EXHAUSTION",
            service="enterprise-ai-platform",
            severity=AlertSeverity.EMERGENCY,
            status=AlertStatus.OPEN,
            summary="Emergency",
            timestamp="2026-09-13T09:00:00Z",
            deployment_identity="dep-001",
        )
    ]
    res = engine.evaluate_signals(alerts)
    assert res.decision == "INCIDENT"
    assert res.severity == IncidentSeverity.P1
    assert res.incident is not None
