"""
Tests for Knowledge & RAG (Phase 5.0) & Memory Integration
"""

import pytest

from app.memory.memory_manager import MemoryManager


@pytest.mark.asyncio
async def test_unified_memory_and_knowledge_retrieval():
    mm = MemoryManager()
    rec = mm.create_memory("Fact: Document RAG chunking uses 512 token windows", organization_id="org_rag")

    matches = await mm.service.retriever.retrieve_semantic("RAG chunking", organization_id="org_rag", top_k=1)
    assert len(matches) >= 1
    assert matches[0]["memory_id"] == rec.memory_id
