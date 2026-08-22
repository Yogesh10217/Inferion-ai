"""Unit tests for MemoryManager storage and retrieval."""

import pytest
from app.knowledge_platform.memory import MemoryManager, MemoryType, MemoryScope


def test_memory_storage_and_retrieval():
    mgr = MemoryManager()
    mem = mgr.store_memory("user_preference_theme", "dark", memory_type=MemoryType.USER_PREFERENCE, scope=MemoryScope.USER, tenant_id="t_mem")

    ret_mem = mgr.get_memory(mem.memory_id)
    assert ret_mem.key == "user_preference_theme"
    assert ret_mem.value == "dark"
