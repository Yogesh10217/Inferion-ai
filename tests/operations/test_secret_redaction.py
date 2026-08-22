"""Unit tests for automated secret and sensitive data redaction in telemetry."""

import pytest
from app.operations.telemetry import TelemetryManager, TelemetryType, TelemetryContext


def test_secret_redaction_in_telemetry_messages():
    mgr = TelemetryManager()

    # Secret API key in message
    msg = "User authenticated with sk-proj-1234567890abcdef1234567890"
    evt = mgr.record_event("auth_service", TelemetryType.LOG, message=msg, context=TelemetryContext(tenant_id="t_sec"))

    assert "sk-proj-1234567890abcdef1234567890" not in evt.message
    assert "[REDACTED]" in evt.message or "sk-" not in evt.message
