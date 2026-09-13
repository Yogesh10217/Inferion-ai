from app.operations.incident_management import IncidentManager, IncidentSeverity
from app.operations.incident_state_machine import IncidentState
from app.operations.sre_metrics import SREMetricsCalculator


def test_sre_metrics_empty():
    calc = SREMetricsCalculator()
    res = calc.calculate_metrics([])
    assert res.status == "NOT_ENOUGH_DATA"
    assert res.total_incidents_analyzed == 0
    assert res.mtta_seconds is None
    assert res.mttr_seconds is None


def test_sre_metrics_with_incidents():
    mgr = IncidentManager()
    inc = mgr.create_incident("P3 Issue", IncidentSeverity.P3)
    mgr.transition_incident(inc.incident_id, IncidentState.TRIAGING)
    mgr.transition_incident(inc.incident_id, IncidentState.CONFIRMED)
    mgr.transition_incident(inc.incident_id, IncidentState.INVESTIGATING)
    mgr.transition_incident(inc.incident_id, IncidentState.MITIGATING)
    mgr.transition_incident(inc.incident_id, IncidentState.RECOVERING)
    mgr.transition_incident(inc.incident_id, IncidentState.RESOLVED)

    calc = SREMetricsCalculator()
    res = calc.calculate_metrics([inc])
    assert res.status == "CALCULATED"
    assert res.total_incidents_analyzed == 1
    assert res.mtta_seconds is not None
    assert res.mttr_seconds is not None
