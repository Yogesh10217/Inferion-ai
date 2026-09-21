"""
Tests for Recovery Orchestrator Module.
"""

from app.reliability.recovery_orchestrator import RecoveryOrchestrator
from app.reliability.reliability_models import FailureSeverity, RecoveryStatus


def test_recovery_orchestration_workflow():
    orchestrator = RecoveryOrchestrator()
    res = orchestrator.orchestrate_recovery(component_name="database", failure_severity=FailureSeverity.HIGH)
    assert res.failure_detected is True
    assert res.incident_id is not None
    assert res.alert_triggered is True
    assert res.recovery_status == RecoveryStatus.RECOVERED
    assert res.recommendation.auto_execution_blocked is True
