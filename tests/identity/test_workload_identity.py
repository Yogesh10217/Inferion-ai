"""Unit tests for WorkloadIdentity short-lived credential issuance."""

import pytest
from app.identity.workload_identity import WorkloadIdentityManager, WorkloadType


def test_workload_identity_credential_issuance():
    mgr = WorkloadIdentityManager()

    wkld = mgr.register_workload("Agent Worker 1", workload_type=WorkloadType.AGENT, tenant_id="t_wkld")
    assert wkld.workload_type == WorkloadType.AGENT

    cred = mgr.issue_credential(wkld.workload_id, ttl_minutes=15)
    assert cred.token_value is not None
    assert cred.workload_id == wkld.workload_id
