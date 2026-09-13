"""
Tests for Reliability Evidence Collector Module.
"""

from app.reliability.reliability_evidence import ReliabilityEvidenceCollector, ReliabilityEvidenceLevel


def test_sha256_evidence_fingerprint_validation():
    collector = ReliabilityEvidenceCollector()
    ev = collector.collect_evidence(
        component="TestComponent",
        event="test_event",
        status="SUCCESS",
        evidence_level=ReliabilityEvidenceLevel.SIMULATION_RUNTIME,
        raw_payload={"key": "value", "secret_pass": "password123"},
    )

    assert ev.fingerprint.startswith("sha256:")
    assert len(ev.fingerprint) == 7 + 64
    assert ev.sanitized_payload.get("secret_pass").startswith("[REDACTED")
