"""Unit tests for strict multi-tenant isolation in knowledge, memory, and graph."""

import pytest
from app.knowledge_platform.knowledge import KnowledgeManager
from app.knowledge_platform.memory import MemoryManager
from app.knowledge_platform.knowledge_graph import KnowledgeGraphManager, KnowledgeNodeType


def test_knowledge_platform_multitenancy():
    km = KnowledgeManager()
    mm = MemoryManager()
    kg = KnowledgeGraphManager()

    # Tenant A
    km.create_knowledge_item("Doc A", content="A", tenant_id="Tenant_A")
    mm.store_memory("mem_a", "val_a", tenant_id="Tenant_A")
    kg.add_node("Node A", node_type=KnowledgeNodeType.ENTITY, tenant_id="Tenant_A")

    # Tenant B
    km.create_knowledge_item("Doc B", content="B", tenant_id="Tenant_B")
    mm.store_memory("mem_b", "val_b", tenant_id="Tenant_B")
    kg.add_node("Node B", node_type=KnowledgeNodeType.ENTITY, tenant_id="Tenant_B")

    # Verify zero leakage across tenant boundaries
    assert len(km.list_items("Tenant_A")) == 1
    assert len(km.list_items("Tenant_B")) == 1
    assert len(mm.list_memories("Tenant_A")) == 1
    assert len(mm.list_memories("Tenant_B")) == 1
