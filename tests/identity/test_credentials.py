"""Unit tests for CredentialManager creation and scoping."""

import pytest
from app.identity.credentials import CredentialManager, CredentialType, CredentialStatus


def test_credential_creation_and_scoping():
    mgr = CredentialManager()

    cred = mgr.create_credential("Prod Service Key", identity_id="service_1", credential_type=CredentialType.SERVICE_TOKEN, tenant_id="t_cred", scopes=["read", "execute"])
    assert cred.credential_type == CredentialType.SERVICE_TOKEN
    assert cred.status == CredentialStatus.ACTIVE
    assert "execute" in cred.scopes
