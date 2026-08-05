import os

PROJECT_ROOT = r"c:\Users\Yogesh E\OneDrive\Desktop\Manjus\llm-inference-engine"
TESTS_DIR = os.path.join(PROJECT_ROOT, "tests", "knowledge")

def write_file(filename, content):
    full_path = os.path.join(TESTS_DIR, filename)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# 1. test_embeddings.py
write_file("test_embeddings.py", """
import pytest
from app.knowledge.embedding_service import OpenAIProvider, EmbeddingCache

@pytest.mark.asyncio
async def test_embedding_provider_cache():
    cache = EmbeddingCache(max_size=100)
    await cache.set("test_key", [0.1, 0.2, 0.3])
    res = await cache.get("test_key")
    assert res == [0.1, 0.2, 0.3]
""")

# 2. test_lifecycle.py
write_file("test_lifecycle.py", """
import pytest
from app.knowledge.lifecycle import DocumentState

def test_document_state_enum():
    assert DocumentState.PENDING == "pending"
    assert DocumentState.INDEXING == "indexing"
    assert DocumentState.ACTIVE == "active"
    assert DocumentState.ERROR == "error"
""")

# 3. test_permissions.py
write_file("test_permissions.py", """
import pytest
from app.knowledge.permissions import DocumentPermissions, Visibility

def test_document_permissions_model():
    perms = DocumentPermissions(visibility=Visibility.PUBLIC)
    assert perms.visibility == "public"
""")

# 4. test_pipeline.py
write_file("test_pipeline.py", """
import pytest
from app.knowledge.pipeline_runner import PipelineRunner
from app.knowledge.pipeline import DocumentContext

@pytest.mark.asyncio
async def test_pipeline_runner_init():
    runner = PipelineRunner(stages=[])
    assert runner.stages == []
    ctx = DocumentContext(document_id="doc1")
    res = await runner.run(ctx)
    assert res.document_id == "doc1"
""")

# 5. test_reranker.py
write_file("test_reranker.py", """
import pytest
from app.knowledge.reranker import DocumentInfo

def test_document_info():
    doc = DocumentInfo(id="1", text="test", score=0.0)
    assert doc.id == "1"
    assert doc.text == "test"
""")

# 6. test_retriever.py
write_file("test_retriever.py", """
import pytest
from app.knowledge.retriever import Retriever

@pytest.mark.asyncio
async def test_retriever_initialization():
    class MockVectorStore: pass
    class MockEmbeddingService: pass
    
    retriever = Retriever(MockVectorStore(), MockEmbeddingService())
    assert retriever.vector_store is not None
""")

# 7. test_versioning.py
write_file("test_versioning.py", """
import pytest
from app.knowledge.versioning import get_next_version
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_get_next_version_mock():
    # Since it requires a db session, we mock the session executing a query
    session = AsyncMock()
    # Mocking the result of session.execute().scalar_one_or_none()
    mock_result = AsyncMock()
    mock_result.scalar_one_or_none.return_value = 2
    session.execute.return_value = mock_result
    
    version = await get_next_version(session, "kb1", "doc1")
    assert version == 3
""")
