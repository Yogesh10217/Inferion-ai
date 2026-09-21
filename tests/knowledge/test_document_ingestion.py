import pytest

from app.knowledge.document_ingestion import DocumentIngestionStage
from app.knowledge.pipeline import DocumentContext


class MockStorageProvider:
    async def get_document(self, document_id: str) -> bytes:
        return b"Hello world! This is a test document."


@pytest.mark.asyncio
async def test_document_ingestion():
    provider = MockStorageProvider()
    stage = DocumentIngestionStage(provider)
    ctx = DocumentContext(document_id="doc1", metadata={"mime_type": "text/plain"})

    result = await stage.process(ctx)
    assert result.parsed_content == "Hello world! This is a test document."
    assert "blocks" in result.metadata
    assert len(result.metadata["blocks"]) == 1
    assert result.metadata["blocks"][0]["text"] == "Hello world! This is a test document."
