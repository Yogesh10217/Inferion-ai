"""Tests for StructuredLogger and sensitive secret redaction."""

import pytest
from app.observability.logging import StructuredLogger, sanitize_value, REDACTED_TEXT
from app.observability.context import ObservabilityContext, with_context


def test_secret_redaction_sanitizer():
    assert sanitize_value("api_key", "secret_key_12345") == REDACTED_TEXT
    assert sanitize_value("user_password", "pass123") == REDACTED_TEXT
    assert sanitize_value("auth_token", "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.e30.signature") == REDACTED_TEXT
    assert sanitize_value("normal_key", "normal_value") == "normal_value"


def test_structured_logger_formatting():
    logger = StructuredLogger(service_name="test-service", component="test-comp")
    ctx = ObservabilityContext(tenant_id="tenant-log-1", agent_id="agent-log-2")

    with with_context(ctx):
        log_entry = logger.info("Test message", extra={"api_key": "supersecret", "normal_param": "hello"})

    assert log_entry["service"] == "test-service"
    assert log_entry["component"] == "test-comp"
    assert log_entry["tenant_id"] == "tenant-log-1"
    assert log_entry["agent_id"] == "agent-log-2"
    assert log_entry["attributes"]["api_key"] == REDACTED_TEXT
    assert log_entry["attributes"]["normal_param"] == "hello"
