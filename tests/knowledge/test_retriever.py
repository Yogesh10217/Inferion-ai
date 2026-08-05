import pytest
from app.knowledge.retriever import Retriever

@pytest.mark.asyncio
async def test_retriever_initialization():
    class MockVectorStore: pass
    class MockEmbeddingService: pass
    
    retriever = Retriever(MockVectorStore(), MockEmbeddingService())
    assert retriever.search_engine is not None
