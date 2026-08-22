"""Unit tests for critical behavioral anomaly triggers and Operations Incident creation."""

import pytest
from app.identity.risk import IdentityRiskEngine, AnomalyType, IdentityRiskSeverity


def test_critical_behavioral_anomaly_triggers_incident():
    mgr = IdentityRiskEngine()

    evt = mgr.record_risk_event(
        identity_id="user_admin",
        anomaly_type=AnomalyType.PRIVILEGE_ESCALATION_ATTEMPT,
        severity=IdentityRiskSeverity.CRITICAL,
        description="Attempted unauthorized root privilege escalation",
        tenant_id="t_anom",
    )

    assert evt.severity == IdentityRiskSeverity.CRITICAL
    assert evt.incident_id is not None  # Auto Operations Incident!
    assert "inc_" in evt.incident_id
