"""Unit tests for GovernanceViolation recording and lifecycle management."""

import pytest
from app.governance_platform.violations import ViolationManager, ViolationType, ViolationSeverity, ViolationStatus


def test_violation_recording_and_status_update():
    mgr = ViolationManager()

    v = mgr.record_violation(
        title="Unapproved API Scope Access",
        violation_type=ViolationType.ACCESS_VIOLATION,
        severity=ViolationSeverity.MEDIUM,
        primary_resource_id="api_gateway",
        tenant_id="t_viol",
    )

    assert v.status == ViolationStatus.DETECTED
    assert v.incident_id is None  # Medium severity -> no auto incident

    updated_v = mgr.update_status(v.violation_id, ViolationStatus.RESOLVED)
    assert updated_v.status == ViolationStatus.RESOLVED
    assert updated_v.resolved_at is not None
