"""Unit tests for Secret Redaction in Intelligence Signals."""

from app.intelligence_platform.signals import IntelligenceSignalManager, SignalSource, SignalType
from app.security.secrets import SecretManager


def test_secret_redaction_in_signals():
    sec_mgr = SecretManager()
    sec_mgr.set_secret("API_KEY_SECRET", "super_secret_api_key_9999")

    sig_mgr = IntelligenceSignalManager(secret_manager=sec_mgr)
    sig = sig_mgr.ingest_signal(
        "t1", SignalSource.SECURITY, SignalType.SECURITY_ALERT, "Leaked key super_secret_api_key_9999 in logs"
    )

    assert "super_secret_api_key_9999" not in sig.message
    assert "[REDACTED_SECRET]" in sig.message
