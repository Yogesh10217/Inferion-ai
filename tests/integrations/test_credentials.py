"""Unit tests for CredentialBroker and SecretManager integration."""

from app.integrations.credentials import CredentialBroker


def test_credential_broker_secret_reference():
    broker = CredentialBroker()
    ref = broker.store_credential("slack_oauth_token", "xoxb-secret-token-12345", tenant_id="t_cred")

    assert ref.credential_id.startswith("cred_")
    assert ref.secret_id is not None
    # Verify plaintext token is NOT exposed in reference object attributes!
    assert "xoxb-secret-token-12345" not in str(ref)
