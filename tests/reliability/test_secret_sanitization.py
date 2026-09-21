"""
Tests for Secret Sanitization in Phase 5.70.
"""

from app.reliability.recovery_audit import RecoveryAuditEngine
from app.reliability.reliability_evidence import ReliabilityEvidenceCollector, ReliabilityEvidenceLevel


def test_secret_canary_sanitization():
    collector = ReliabilityEvidenceCollector()
    canaries = [
        "password123",
        "canary_secret",
        "admin123",
        "super_secret_test_value",
    ]

    raw_payload = {
        "db_pass": "password123",
        "api_key": "canary_secret",
        "admin_password": "admin123",
        "token": "super_secret_test_value",
        "safe_field": "normal_value",
    }

    ev = collector.collect_evidence(
        component="SecretTestComponent",
        event="test_secret_event",
        status="SUCCESS",
        evidence_level=ReliabilityEvidenceLevel.SIMULATION_RUNTIME,
        raw_payload=raw_payload,
    )

    # Check evidence payload
    for secret in canaries:
        assert secret not in str(ev.sanitized_payload)

    # Audit records check
    audit_engine = RecoveryAuditEngine()
    audit_res = audit_engine.audit_evidence_records(collector.get_all_evidence())
    assert audit_res.valid is True
    for secret in canaries:
        assert secret not in str(audit_res)
