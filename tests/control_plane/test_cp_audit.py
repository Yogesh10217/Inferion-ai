"""Unit tests for AdministrativeAuditLedger."""

import pytest
from app.control_plane.admin_audit import AdministrativeAuditLedger
from app.security.secrets import SecretManager


def test_administrative_audit_recording_and_redaction():
    secret_mgr = SecretManager()
    secret_mgr.register_secret_value("secret_key_value_999")

    ledger = AdministrativeAuditLedger(secret_manager=secret_mgr)

    event = ledger.record_action(
        actor_id="admin_1",
        action="update_config",
        target_resource_id="ws_10",
        tenant_id="tenant_audit",
        new_state={"token": "secret_key_value_999", "env": "prod"},
    )

    assert event.actor_id == "admin_1"
    assert event.new_state["token"] == "[REDACTED_SECRET]"
    assert event.new_state["env"] == "prod"
