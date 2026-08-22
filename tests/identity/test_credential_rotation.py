"""Unit tests for CredentialManager automated credential rotation."""

import pytest
from app.identity.credentials import CredentialManager, CredentialStatus


def test_credential_rotation_and_revocation():
    mgr = CredentialManager()

    cred = mgr.create_credential("DB Access Token", identity_id="db_user", tenant_id="t_rot")
    assert cred.status == CredentialStatus.ACTIVE

    # Rotate
    new_cred = mgr.rotate_credential(cred.credential_id)
    assert mgr.get_credential(cred.credential_id).status == CredentialStatus.ROTATED
    assert new_cred.status == CredentialStatus.ACTIVE

    # Revoke new credential
    rev_cred = mgr.revoke_credential(new_cred.credential_id, reason="Security audit")
    assert rev_cred.status == CredentialStatus.REVOKED
