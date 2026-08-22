"""Unit tests for strict multi-tenant isolation across identity resources."""

import pytest
from app.identity.identity import IdentityManager
from app.identity.session import SessionManager
from app.identity.credentials import CredentialManager
from app.identity.privileged_access import PrivilegedAccessManager, PrivilegedRole


def test_strict_multi_tenant_isolation():
    i_mgr = IdentityManager()
    s_mgr = SessionManager()
    c_mgr = CredentialManager()
    p_mgr = PrivilegedAccessManager()

    # Tenant A
    id_A = i_mgr.create_identity("user_A", tenant_id="Tenant_A")
    s_mgr.create_session(id_A.identity_id, tenant_id="Tenant_A")
    c_mgr.create_credential("cred_A", identity_id=id_A.identity_id, tenant_id="Tenant_A")
    p_mgr.request_privileged_access(id_A.identity_id, PrivilegedRole.TENANT_ADMIN, tenant_id="Tenant_A")

    # Tenant B
    id_B = i_mgr.create_identity("user_B", tenant_id="Tenant_B")
    s_mgr.create_session(id_B.identity_id, tenant_id="Tenant_B")
    c_mgr.create_credential("cred_B", identity_id=id_B.identity_id, tenant_id="Tenant_B")
    p_mgr.request_privileged_access(id_B.identity_id, PrivilegedRole.TENANT_ADMIN, tenant_id="Tenant_B")

    # Verify zero cross-tenant leakage
    assert len(i_mgr.list_identities("Tenant_A")) == 1
    assert len(i_mgr.list_identities("Tenant_B")) == 1
    assert len(s_mgr.list_sessions("Tenant_A")) == 1
    assert len(s_mgr.list_sessions("Tenant_B")) == 1
