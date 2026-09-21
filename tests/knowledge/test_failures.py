from unittest.mock import AsyncMock

import pytest

from app.knowledge.chunking import ChunkingStage, ChunkingStrategy
from app.knowledge.document_ingestion import DocumentIngestionStage
from app.knowledge.embedding_service import EmbeddingStage
from app.knowledge.pipeline import DocumentContext, PipelineStatus
from app.knowledge.pipeline_runner import PipelineRunner, VectorStoreStage


class MockStorageProvider:
    async def get_document(self, document_id: str) -> bytes:
        return b"This is a test document."


@pytest.mark.asyncio
async def test_failure_embedding_provider_unavailable():
    provider = AsyncMock()
    provider.get_embeddings.side_effect = Exception("Embedding Provider Unavailable")

    pipeline = PipelineRunner(
        [
            DocumentIngestionStage(MockStorageProvider()),
            ChunkingStage(strategy=ChunkingStrategy.RECURSIVE, chunk_size=20),
            EmbeddingStage(provider),
            VectorStoreStage(AsyncMock()),
        ]
    )

    context = DocumentContext(document_id="doc_fail1", metadata={"mime_type": "text/plain"})
    context = await pipeline.run(context)

    assert context.status == PipelineStatus.FAILED
    assert len(context.errors) > 0
    assert any("Embedding Provider Unavailable" in err for err in context.errors)


@pytest.mark.asyncio
async def test_failure_vector_db_unavailable():
    provider = AsyncMock()
    provider.get_embeddings.return_value = [[0.1, 0.2, 0.3]]
    provider.get_dimensions.return_value = 3

    class FailingVectorStore:
        async def add(self, embeddings, collection_name):
            raise Exception("Vector DB Connection Error")

    pipeline = PipelineRunner(
        [
            DocumentIngestionStage(MockStorageProvider()),
            ChunkingStage(strategy=ChunkingStrategy.RECURSIVE, chunk_size=20),
            EmbeddingStage(provider),
            VectorStoreStage(FailingVectorStore()),
        ]
    )

    context = DocumentContext(document_id="doc_fail2", metadata={"mime_type": "text/plain"})
    context = await pipeline.run(context)

    assert context.status == PipelineStatus.FAILED
    assert len(context.errors) > 0
    assert any("Vector DB Connection Error" in err for err in context.errors)


@pytest.mark.asyncio
async def test_failure_storage_unavailable():
    class FailingStorageProvider:
        async def get_document(self, document_id: str) -> bytes:
            raise Exception("Storage Service Unavailable")

    pipeline = PipelineRunner(
        [
            DocumentIngestionStage(FailingStorageProvider()),
        ]
    )

    context = DocumentContext(document_id="doc_fail3")
    context = await pipeline.run(context)

    assert context.status == PipelineStatus.FAILED
    assert len(context.errors) > 0
    assert any("Storage Service Unavailable" in err for err in context.errors)
