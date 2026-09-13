"""
Tests for Integration with Phase 5.68 Incident & Alert Engines (Phase 5.69).
"""

import pytest
from app.security_operations.security_event_detection import SecurityEventDetector
from app.security_operations.security_threat_classifier import SecurityThreatClassifier

try:
    from app.operations.incident_management import IncidentManager
    from app.operations.alert_engine import AlertEngine
    SRE_AVAILABLE = True
except ImportError:
    SRE_AVAILABLE = False


def test_sre_integration_when_available():
    if not SRE_AVAILABLE:
        pytest.skip("Phase 5.68 SRE modules not present")

    incident_mgr = IncidentManager()
    alert_engine = AlertEngine()

    detector = SecurityEventDetector(incident_manager=incident_mgr, alert_engine=alert_engine)
    event = detector.record_event(
        event_type="UNAUTHORIZED_ACCESS_ATTEMPT",
        severity="CRITICAL",
        description="Brute force login detected on production endpoint",
        source="AuthModule",
    )

    assert event.event_id in detector.get_events()
    # Check that incident manager logged an incident
    active_incidents = incident_mgr.get_active_incidents()
    assert len(active_incidents) >= 1
