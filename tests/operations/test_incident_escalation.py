from app.operations.incident_escalation import IncidentEscalationEngine, NotificationReadiness
from app.operations.incident_management import IncidentManager, IncidentSeverity


def test_incident_escalation():
    mgr = IncidentManager()
    inc = mgr.create_incident("Minor issue", IncidentSeverity.P4)
    engine = IncidentEscalationEngine()

    res = engine.evaluate_escalation(inc, unresolved_minutes=35)
    assert res.is_escalated
    assert res.current_severity == IncidentSeverity.P3
    assert res.notification_status == NotificationReadiness.NOTIFICATION_SIMULATED
