"""
Tests for Recovery Audit Engine Module.
"""

from app.reliability.recovery_audit import RecoveryAuditEngine
from app.reliability.reliability_evidence import ReliabilityEvidenceCollector, ReliabilityEvidenceLevel


def test_evidence_tampering_detection():
    collector = ReliabilityEvidenceCollector()
    ev1 = collector.collect_evidence("Comp", "event1", "SUCCESS", ReliabilityEvidenceLevel.SIMULATION_RUNTIME, {"a": 1})
    collector.collect_evidence("Comp", "event2", "SUCCESS", ReliabilityEvidenceLevel.SIMULATION_RUNTIME, {"b": 2})

    audit_engine = RecoveryAuditEngine()
    res_valid = audit_engine.audit_evidence_records(collector.get_all_evidence())
    assert res_valid.valid is True
    assert res_valid.tampering_detected is False

    # Simulate tampering by altering payload without updating fingerprint
    ev1.sanitized_payload["a"] = 999
    res_tampered = audit_engine.audit_evidence_records(collector.get_all_evidence())
    assert res_tampered.valid is False
    assert res_tampered.tampering_detected is True
