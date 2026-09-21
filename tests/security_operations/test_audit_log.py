"""
Tests for Security Audit Logger (Phase 5.69).
"""

from app.security_operations.audit_log import SecurityAuditLogger


def test_audit_logging_chain():
    logger = SecurityAuditLogger()
    rec1 = logger.log_event("POLICY_CHECK", "INFO", "Checked policy", "test_actor", "res_1")
    rec2 = logger.log_event("POLICY_VIOLATION", "WARNING", "Violation detected", "test_actor", "res_1")

    assert rec1.record_hash.startswith("sha256:")
    assert rec2.record_hash.startswith("sha256:")
    assert rec2.previous_hash == rec1.record_hash
    assert len(logger.get_records()) == 2
