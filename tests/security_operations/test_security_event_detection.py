"""
Tests for Security Event Detection (Phase 5.69).
"""

from app.security_operations.security_event_detection import SecurityEvent, SecurityEventDetector


def test_security_event_detection_routing():
    detector = SecurityEventDetector()
    event = detector.record_event(
        event_type="UNAUTHORIZED_ACCESS_ATTEMPT",
        severity="HIGH",
        description="Repeated failed logins detected from IP 192.168.1.100",
        source="AuthModule",
    )
    assert isinstance(event, SecurityEvent)
    assert event.event_id.startswith("SECEVT-")
    assert event.fingerprint.startswith("sha256:")
