"""Unit tests for IdentityRiskEngine event recording."""

from app.identity.risk import AnomalyType, IdentityRiskEngine, IdentityRiskSeverity


def test_identity_risk_event_recording():
    mgr = IdentityRiskEngine()

    evt = mgr.record_risk_event(
        identity_id="user_test",
        anomaly_type=AnomalyType.UNUSUAL_IP,
        severity=IdentityRiskSeverity.MEDIUM,
        description="Login from new IP address",
        tenant_id="t_risk",
    )

    assert evt.identity_id == "user_test"
    assert evt.anomaly_type == AnomalyType.UNUSUAL_IP
    assert evt.severity == IdentityRiskSeverity.MEDIUM
    assert evt.incident_id is None
