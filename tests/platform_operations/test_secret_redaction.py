"""Unit tests for Secret Sanitization in Operational Signals."""

from app.platform_operations.signals import SignalManager, SignalSource, SignalType
from app.security.secrets import SecretManager


def test_secret_sanitization_in_signal_message_and_payload():
    sec_mgr = SecretManager()
    sec_mgr.set_secret("DB_PASSWORD", "super_secret_password_999")

    sig_mgr = SignalManager()
    sig_mgr.normalizer.secret_manager = sec_mgr

    sig = sig_mgr.ingest_signal(
        tenant_id="t1",
        source=SignalSource.LOGS,
        signal_type=SignalType.LOG_ERROR,
        message="Failed connection with password super_secret_password_999",
        payload={"secret_key": "super_secret_password_999"},
    )

    assert "super_secret_password_999" not in sig.message
    assert "[REDACTED_SECRET]" in sig.message
    assert sig.payload["secret_key"] == "[REDACTED_SECRET]"
