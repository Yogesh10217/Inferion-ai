"""
Tests for Audit Integrity Engine (Phase 5.69).
"""

import pytest
from app.security_operations.audit_log import SecurityAuditLogger
from app.security_operations.audit_integrity import AuditIntegrityEngine, AuditIntegrityResult


def test_audit_integrity_valid_chain():
    logger = SecurityAuditLogger()
    logger.log_event("EVENT_1", "INFO", "Desc 1", "actor1", "res1")
    logger.log_event("EVENT_2", "INFO", "Desc 2", "actor2", "res2")

    engine = AuditIntegrityEngine(logger)
    result = engine.validate_audit_chain()
    assert isinstance(result, AuditIntegrityResult)
    assert result.is_valid is True
    assert result.tampering_detected is False


def test_audit_integrity_tamper_detection():
    logger = SecurityAuditLogger()
    logger.log_event("EVENT_1", "INFO", "Desc 1", "actor1", "res1")
    logger.log_event("EVENT_2", "INFO", "Desc 2", "actor2", "res2")

    # Tamper with event 1
    logger._records[0].description = "Tampered description"

    engine = AuditIntegrityEngine(logger)
    result = engine.validate_audit_chain()
    assert result.is_valid is False
    assert result.tampering_detected is True
