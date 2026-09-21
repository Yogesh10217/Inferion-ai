"""
Tests for Memory Retriever Engine
"""

import pytest

from app.memory.memory_embeddings import MemoryEmbeddingService
from app.memory.memory_retriever import MemoryRetriever
from app.memory.memory_vector_store import MemoryVectorStore


@pytest.mark.asyncio
async def test_memory_retriever_semantic_search():
    vs = MemoryVectorStore()
    emb = MemoryEmbeddingService()
    retriever = MemoryRetriever(vector_store=vs, embedding_service=emb)

    v1 = await emb.get_embedding("FastAPI web framework")
    v2 = await emb.get_embedding("PostgreSQL relational database")

    vs.add("mem_1", v1, {"content": "FastAPI web framework", "importance_score": 0.8}, "org_1", "ws_1")
    vs.add("mem_2", v2, {"content": "PostgreSQL relational database", "importance_score": 0.9}, "org_1", "ws_1")

    results = await retriever.retrieve_semantic(
        "FastAPI framework", organization_id="org_1", workspace_id="ws_1", top_k=2
    )
    assert len(results) == 2
    assert results[0]["memory_id"] == "mem_1"
