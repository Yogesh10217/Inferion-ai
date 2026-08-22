"""Unit tests for SensitiveDataDetector and RedactionEngine."""

import pytest
from app.data_fabric.data_security import SensitiveDataDetector, RedactionEngine, SensitiveDataAction


def test_sensitive_data_detection_and_redaction():
    detector = SensitiveDataDetector()
    redactor = RedactionEngine(detector=detector)

    payload = {
        "api_key": "sk-live-1234567890abcdef12345",
        "email": "john.doe@example.com",
        "message": "User card is 4111111111111111",
    }

    detections = detector.detect_sensitive_data(payload)
    assert len(detections) >= 1

    # Redact secret payload
    sanitized = redactor.sanitize(payload, action=SensitiveDataAction.REDACT)
    assert sanitized["api_key"] == "[REDACTED_SECRET]"
