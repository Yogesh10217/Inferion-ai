from app.operations.incident_management import IncidentManager, IncidentSeverity
from app.operations.incident_state_machine import IncidentState


def test_incident_management_lifecycle():
    mgr = IncidentManager()
    inc = mgr.create_incident(
        title="Test Incident",
        severity=IncidentSeverity.P2,
        summary="Major degradation",
    )
    assert inc.state == IncidentState.DETECTED
    assert inc.incident_id in mgr.active_incidents

    mgr.transition_incident(inc.incident_id, IncidentState.TRIAGING)
    assert inc.state == IncidentState.TRIAGING

    mgr.transition_incident(inc.incident_id, IncidentState.CONFIRMED)
    mgr.transition_incident(inc.incident_id, IncidentState.INVESTIGATING)
    mgr.transition_incident(inc.incident_id, IncidentState.MITIGATING)
    mgr.transition_incident(inc.incident_id, IncidentState.RECOVERING)
    mgr.transition_incident(inc.incident_id, IncidentState.MONITORING)
    mgr.transition_incident(inc.incident_id, IncidentState.RESOLVED)
    mgr.transition_incident(inc.incident_id, IncidentState.CLOSED)

    assert inc.state == IncidentState.CLOSED
    assert inc.incident_id in mgr.closed_incidents
