"""
Tests for Multi-Tenant Scoping & Isolation
"""

import pytest
from app.memory.memory_manager import MemoryManager
from app.memory.exceptions import TenantMemoryIsolationError


def test_tenant_isolation_in_memory_platform():
    mm = MemoryManager()
    m1 = mm.create_memory("Org 1 Secret Data", organization_id="org_alpha", workspace_id="ws_1")
    m2 = mm.create_memory("Org 2 Secret Data", organization_id="org_beta", workspace_id="ws_1")

    res_alpha = mm.list_memories(organization_id="org_alpha")
    assert len(res_alpha) == 1
    assert res_alpha[0].memory_id == m1.memory_id

    res_beta = mm.list_memories(organization_id="org_beta")
    assert len(res_beta) == 1
    assert res_beta[0].memory_id == m2.memory_id

    with pytest.raises(TenantMemoryIsolationError):
        mm.get_memory(m1.memory_id, organization_id="org_beta")
