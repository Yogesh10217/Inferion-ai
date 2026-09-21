"""
Tests for Unified Memory Store
"""

import pytest

from app.memory.exceptions import TenantMemoryIsolationError
from app.memory.memory_store import MemoryItemRecord, MemoryStore
from app.memory.memory_types import MemoryStatus, MemoryType


def test_memory_store_crud():
    store = MemoryStore()
    rec = MemoryItemRecord(
        organization_id="org_1",
        workspace_id="ws_1",
        memory_type=MemoryType.SEMANTIC,
        content="PostgreSQL is the main DB",
    )
    saved = store.save(rec)
    assert saved.memory_id is not None

    fetched = store.get(saved.memory_id, organization_id="org_1")
    assert fetched.content == "PostgreSQL is the main DB"

    updated = store.update(saved.memory_id, organization_id="org_1", content="PostgreSQL 16 is DB")
    assert updated.content == "PostgreSQL 16 is DB"

    archived = store.archive(saved.memory_id, organization_id="org_1")
    assert archived.status == MemoryStatus.ARCHIVED

    store.delete(saved.memory_id, organization_id="org_1")
    assert store.get(saved.memory_id, organization_id="org_1").status == MemoryStatus.DELETED


def test_memory_store_tenant_isolation():
    store = MemoryStore()
    rec = MemoryItemRecord(
        organization_id="org_1", workspace_id="ws_1", memory_type=MemoryType.PROFILE, content="User prefers Python"
    )
    saved = store.save(rec)

    with pytest.raises(TenantMemoryIsolationError):
        store.get(saved.memory_id, organization_id="org_other")
