"""
Tests for Integration with Phase 5.68 Operations.
"""

from app.operations import IncidentManager
from app.operations.alerting import AlertManager
from app.reliability.recovery_orchestrator import RecoveryOrchestrator


def test_integration_with_phase_5_68_operations():
    inc_mgr = IncidentManager()
    alt_mgr = AlertManager()
    orchestrator = RecoveryOrchestrator(incident_manager=inc_mgr, alert_manager=alt_mgr)

    res = orchestrator.orchestrate_recovery(component_name="postgresql")
    assert res.incident_id in inc_mgr.active_incidents
    assert len(alt_mgr.list_alerts()) > 0
