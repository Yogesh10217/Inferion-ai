"""Unit tests for critical violation automatic operations incident integration."""

from app.governance_platform.violations import ViolationManager, ViolationSeverity, ViolationType


def test_critical_violation_triggers_operations_incident():
    mgr = ViolationManager()

    v = mgr.record_violation(
        title="Unauthorized Database Export Attempt",
        violation_type=ViolationType.DATA_VIOLATION,
        severity=ViolationSeverity.CRITICAL,
        primary_resource_id="db_finance",
        tenant_id="t_crit",
    )

    assert v.severity == ViolationSeverity.CRITICAL
    assert v.incident_id is not None  # Auto-created Operations Incident!
    assert "inc_" in v.incident_id
