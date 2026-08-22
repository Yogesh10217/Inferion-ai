"""Unit tests for agent private memory scope isolation."""

import pytest
from app.knowledge_platform.memory import MemoryManager, MemoryType, MemoryScope
from app.knowledge_platform.exceptions import KnowledgeAccessDeniedException


def test_agent_private_memory_isolation():
    mgr = MemoryManager()
    mem = mgr.store_memory(
        key="secret_agent_notes",
        value="Agent Alpha Internal Strategy",
        memory_type=MemoryType.AGENT,
        scope=MemoryScope.AGENT,
        owner_agent_id="agent_alpha",
        tenant_id="t_misol",
    )

    # Agent Alpha accesses own memory -> Success
    mem_alpha = mgr.get_memory(mem.memory_id, requesting_agent_id="agent_alpha")
    assert mem_alpha.value == "Agent Alpha Internal Strategy"

    # Agent Beta attempts to access Agent Alpha private memory -> Exception!
    with pytest.raises(KnowledgeAccessDeniedException):
        mgr.get_memory(mem.memory_id, requesting_agent_id="agent_beta")
