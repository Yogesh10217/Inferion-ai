"""
Tests for Memory Vector Store
"""

import pytest
from app.memory.memory_vector_store import MemoryVectorStore
from app.memory.exceptions import TenantMemoryIsolationError


def test_memory_vector_store_operations():
    vs = MemoryVectorStore()
    vec1 = [1.0, 0.0, 0.0]
    vec2 = [0.0, 1.0, 0.0]

    vs.add("m1", vec1, {"name": "item1"}, organization_id="org_1", workspace_id="ws_1")
    vs.add("m2", vec2, {"name": "item2"}, organization_id="org_1", workspace_id="ws_1")

    res = vs.similarity_search([0.9, 0.1, 0.0], organization_id="org_1", workspace_id="ws_1", top_k=2)
    assert len(res) == 2
    assert res[0]["memory_id"] == "m1"
    assert res[0]["score"] > res[1]["score"]

    assert vs.delete("m1") is True
    res_after = vs.similarity_search([0.9, 0.1, 0.0], organization_id="org_1", workspace_id="ws_1", top_k=2)
    assert len(res_after) == 1
    assert res_after[0]["memory_id"] == "m2"


def test_memory_vector_store_tenant_isolation():
    vs = MemoryVectorStore()
    with pytest.raises(TenantMemoryIsolationError):
        vs.add("m1", [1.0, 0.0], {"name": "item1"}, organization_id="")
