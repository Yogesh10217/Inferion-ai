"""
Tests for Security Exception Manager (Phase 5.69).
"""

from datetime import datetime, timedelta, timezone

from app.security_operations.security_exception_management import (
    SecurityException,
    SecurityExceptionManager,
    SecurityExceptionStatus,
)


def test_exception_creation_and_active_check():
    mgr = SecurityExceptionManager()
    exp = mgr.grant_exception(
        vulnerability_id="VULN-1234",
        policy_id="SEC-POL-001",
        reason="Mitigated by WAF rules",
        requested_by="security_team",
        duration_days=7,
    )
    assert isinstance(exp, SecurityException)
    assert exp.is_active is True
    assert len(mgr.get_active_exceptions()) == 1


def test_expired_exception():
    mgr = SecurityExceptionManager()
    past_expiry = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    exp = SecurityException(
        exception_id="EX-TEST",
        vulnerability_id="VULN-9999",
        policy_id="SEC-POL-002",
        reason="Expired test",
        requested_by="tester",
        granted_at=past_expiry,
        expires_at=past_expiry,
        status=SecurityExceptionStatus.APPROVED,
    )
    mgr._exceptions[exp.exception_id] = exp
    active = mgr.get_active_exceptions()
    assert len(active) == 0
    assert exp.is_active is False
