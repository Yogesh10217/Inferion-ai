import logging
import time
import json
from typing import List, Dict, Any, Optional

from app.knowledge.pipeline import PipelineStage, DocumentContext, PipelineStatus
from app.knowledge.document_ingestion import DocumentIngestionStage, StorageProvider
from app.knowledge.chunking import ChunkingStage, ChunkingStrategy
from app.knowledge.embedding_service import EmbeddingStage, ProviderFactory
from app.knowledge.vector_store import VectorStore
from app.monitoring.metrics import (
    knowledge_documents_total,
    knowledge_chunks_total,
    knowledge_index_duration_seconds,
    knowledge_errors_total,
    vector_storage_bytes
)
from app.billing.tracker import tracker

logger = logging.getLogger(__name__)

class VectorStoreStage(PipelineStage):
    """Saves document chunks and embeddings to the vector store."""
    def __init__(self, vector_store: VectorStore, collection_name: str = "default"):
        self.vector_store = vector_store
        self.collection_name = collection_name

    async def process(self, context: DocumentContext) -> DocumentContext:
        if not context.chunks:
            context.errors.append("No chunks to store.")
            return context
            
        embeddings_to_store = []
        for chunk in context.chunks:
            if "embedding" not in chunk:
                context.errors.append(f"Chunk {chunk.get('chunk_id')} is missing an embedding.")
                return context
            
            # Prepare metadata mapping correctly
            metadata = {k: v for k, v in chunk.items() if k not in ("chunk_id", "embedding")}
            embeddings_to_store.append({
                "id": chunk["chunk_id"],
                "vector": chunk["embedding"],
                "metadata": metadata
            })
            
        try:
            await self.vector_store.add(embeddings_to_store, self.collection_name)
            
            # Calculate approx storage bytes
            storage_size = 0
            for item in embeddings_to_store:
                storage_size += len(item["vector"]) * 4
                storage_size += len(json.dumps(item["metadata"]).encode("utf-8"))
                
            tracker.track_vector_storage(storage_size)
            vector_storage_bytes.inc(storage_size)
            
        except Exception as e:
            context.errors.append(f"Failed to save to vector store: {e}")
            
        return context

class PipelineRunner:
    """Executes a series of pipeline stages."""
    
    def __init__(self, stages: List[PipelineStage]):
        self.stages = stages

    async def run(self, context: DocumentContext) -> DocumentContext:
        """Runs the document context through all configured stages."""
        context.status = PipelineStatus.IN_PROGRESS
        start_time = time.time()
        
        try:
            for stage in self.stages:
                logger.info(f"Running stage: {stage.__class__.__name__} for document {context.document_id}")
                context = await stage.process(context)
                if context.errors:
                    logger.error(f"Stage {stage.__class__.__name__} failed for document {context.document_id}: {context.errors}")
                    context.status = PipelineStatus.FAILED
                    break
            
            if not context.errors:
                context.status = PipelineStatus.COMPLETED
                logger.info(f"Pipeline completed successfully for document {context.document_id}")
                
        except Exception as e:
            logger.exception(f"Pipeline failed for document {context.document_id}")
            context.errors.append(str(e))
            context.status = PipelineStatus.FAILED
            
        duration = time.time() - start_time
        
        # Track metrics
        if context.status == PipelineStatus.COMPLETED:
            knowledge_documents_total.inc()
            if context.chunks:
                knowledge_chunks_total.inc(len(context.chunks))
            knowledge_index_duration_seconds.observe(duration)
        else:
            knowledge_errors_total.inc()
            
        # Track billing
        tracker.track_ingestion_job()
        tracker.track_indexing_duration(duration)
            
        return context

def build_end_to_end_pipeline(
    storage_provider: StorageProvider,
    embedding_provider: ProviderFactory,
    vector_store: VectorStore,
    collection_name: str = "default",
    chunk_strategy: ChunkingStrategy = ChunkingStrategy.TOKEN_AWARE
) -> PipelineRunner:
    """Creates a configured end-to-end knowledge ingestion pipeline."""
    return PipelineRunner([
        DocumentIngestionStage(storage_provider=storage_provider),
        ChunkingStage(strategy=chunk_strategy),
        EmbeddingStage(provider_factory=embedding_provider),
        VectorStoreStage(vector_store=vector_store, collection_name=collection_name)
    ])
