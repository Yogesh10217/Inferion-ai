"""Unit tests for IdentityAuditManager event logging."""

import pytest
from app.identity.audit import IdentityAuditManager


def test_identity_audit_logging():
    mgr = IdentityAuditManager()

    evt = mgr.record_event(
        event_type="AUTHENTICATION",
        identity_id="user_1",
        action="login",
        resource_id="auth_endpoint",
        outcome="SUCCESS",
        tenant_id="t_aud",
    )

    assert evt.identity_id == "user_1"
    assert evt.event_type == "AUTHENTICATION"
    assert evt.outcome == "SUCCESS"
