"""
Tests for Security Threat Classifier (Phase 5.69).
"""

import pytest
from app.security_operations.security_threat_classifier import SecurityThreatClassifier, SecurityThreat


def test_threat_classifier_recommendation():
    classifier = SecurityThreatClassifier()
    threat = classifier.classify_threat(
        threat_type="EXPLOIT_ATTEMPT",
        severity="CRITICAL",
        description="SQL Injection attempt detected in API query param",
        affected_component="API Gateway",
    )
    assert isinstance(threat, SecurityThreat)
    assert threat.decision == "BLOCK_RELEASE"
    assert threat.auto_execution_blocked is True
    assert threat.fingerprint.startswith("sha256:")
