import pytest

from app.knowledge.chunking import ChunkingStage, ChunkingStrategy
from app.knowledge.pipeline import DocumentContext


@pytest.mark.asyncio
async def test_chunking_stage():
    stage = ChunkingStage(strategy=ChunkingStrategy.RECURSIVE, chunk_size=10, chunk_overlap=2)
    ctx = DocumentContext(
        document_id="doc1", parsed_content="Hello world this is a test document with more than ten chars."
    )
    result = await stage.process(ctx)
    assert len(result.chunks) > 1
    assert result.chunks[0]["text"].startswith("Hello")
