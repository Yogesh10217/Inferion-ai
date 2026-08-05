import pytest
import time
from app.knowledge.chunking import ChunkingStage, ChunkingStrategy
from app.knowledge.pipeline import DocumentContext

@pytest.mark.asyncio
async def test_chunking_performance_large_document():
    stage = ChunkingStage(strategy=ChunkingStrategy.TOKEN_AWARE, chunk_size=500, chunk_overlap=50)
    
    # Generate a large document (approx 10MB of text)
    large_text = "This is a performance testing sentence to simulate a large document structure. " * 100000
    
    context = DocumentContext(document_id="perf_doc_1", parsed_content=large_text)
    
    start_time = time.time()
    context = await stage.process(context)
    end_time = time.time()
    
    processing_time = end_time - start_time
    
    assert len(context.errors) == 0
    assert len(context.chunks) > 1000
    # The chunking stage should process 10MB under a reasonable threshold (e.g. 5 seconds)
    assert processing_time < 5.0, f"Chunking took too long: {processing_time} seconds"

@pytest.mark.asyncio
async def test_chunking_performance_many_small_documents():
    stage = ChunkingStage(strategy=ChunkingStrategy.RECURSIVE, chunk_size=200)
    
    small_text = "Small document content for performance. " * 20
    
    start_time = time.time()
    for i in range(100):
        context = DocumentContext(document_id=f"small_doc_{i}", parsed_content=small_text)
        await stage.process(context)
    end_time = time.time()
    
    processing_time = end_time - start_time
    
    # Processing 100 small documents should take less than 2 seconds
    assert processing_time < 2.0, f"Processing 100 small docs took too long: {processing_time} seconds"
