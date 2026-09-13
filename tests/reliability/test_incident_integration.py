"""
Tests for Reliability Incident Integration Module.
"""

from app.reliability.reliability_incident_integration import ReliabilityIncidentIntegration


def test_incident_creation_and_alert_deduplication():
    integration = ReliabilityIncidentIntegration()

    # First signal -> triggers alert & creates incident
    res1 = integration.process_reliability_signal("postgresql", "connection_error_rate", 0.9, 0.1, severity="CRITICAL")
    assert res1.incident_created is True
    assert res1.incident_id is not None
    assert res1.alert_deduplicated is False
    assert res1.recovery_recommendation.auto_execution_blocked is True

    # Duplicate signal -> deduplicated, no duplicate incident
    res2 = integration.process_reliability_signal("postgresql", "connection_error_rate", 0.95, 0.1, severity="CRITICAL")
    assert res2.incident_created is False
    assert res2.alert_deduplicated is True
