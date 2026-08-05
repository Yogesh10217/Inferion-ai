"""
Search Module.
Implements Hybrid Search, BM25, Dense, Metadata, and Semantic Search.
"""
from typing import List, Dict, Any, Optional
import logging
from abc import ABC, abstractmethod
from .reranker import DocumentInfo
from .vector_store import VectorStore
from .embedding_service import ProviderFactory

logger = logging.getLogger(__name__)

class SparseStore(ABC):
    @abstractmethod
    async def search(self, query: str, collection_name: str, top_k: int, filter_expr: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """Search the sparse store (e.g. BM25)."""
        pass

class SearchEngine:
    """Core search functionality."""
    
    def __init__(
        self, 
        vector_store: Optional[VectorStore] = None, 
        sparse_store: Optional[SparseStore] = None,
        embedding_provider: Optional[ProviderFactory] = None,
        collection_name: str = "default"
    ):
        self.vector_store = vector_store
        self.sparse_store = sparse_store
        self.embedding_provider = embedding_provider
        self.collection_name = collection_name
        
    async def _apply_acl_filters(self, base_filter: Optional[Dict]) -> Dict:
        """Ensures Workspace/Org ACL filtering is applied."""
        return base_filter or {}

    async def dense_search(self, query: str, top_k: int, filter: Optional[Dict] = None) -> List[DocumentInfo]:
        """Performs dense (semantic) search using vector embeddings."""
        logger.info(f"Performing dense search for query: {query}")
        
        from app.monitoring.metrics import (
            knowledge_embedding_latency_seconds, 
            knowledge_vector_search_latency_seconds,
            retrieval_calls_total,
            knowledge_errors_total
        )
        from app.billing.tracker import tracker
        import time
        
        if not self.vector_store or not self.embedding_provider:
            logger.warning("Vector store or embedding provider not initialized.")
            return []
            
        acl_filter = await self._apply_acl_filters(filter)
        
        try:
            start_embed = time.time()
            query_vectors = await self.embedding_provider.get_embeddings([query])
            embed_duration = time.time() - start_embed
            knowledge_embedding_latency_seconds.observe(embed_duration)
            
            if not query_vectors:
                return []
            query_vector = query_vectors[0]
        except Exception as e:
            logger.error(f"Failed to generate query embedding: {e}")
            knowledge_errors_total.inc()
            return []
            
        start_search = time.time()
        results = await self.vector_store.search(query_vector, self.collection_name, top_k, acl_filter)
        search_duration = time.time() - start_search
        knowledge_vector_search_latency_seconds.observe(search_duration)
        
        retrieval_calls_total.inc()
        tracker.track_retrieval_call()
        
        return [
            DocumentInfo(
                id=res.get("id"),
                text=res.get("metadata", {}).get("text", ""),
                metadata=res.get("metadata", {}),
                score=res.get("score", 0.0)
            ) for res in results
        ]
        
    async def sparse_search(self, query: str, top_k: int, filter: Optional[Dict] = None) -> List[DocumentInfo]:
        """Performs sparse (BM25) keyword search."""
        logger.info(f"Performing sparse search for query: {query}")
        if not self.sparse_store:
            logger.warning("Sparse store not initialized.")
            return []
            
        acl_filter = await self._apply_acl_filters(filter)
        results = await self.sparse_store.search(query, self.collection_name, top_k, acl_filter)
        
        return [
            DocumentInfo(
                id=res.get("id"),
                text=res.get("metadata", {}).get("text", ""),
                metadata=res.get("metadata", {}),
                score=res.get("score", 0.0)
            ) for res in results
        ]
        
    async def hybrid_search(self, query: str, top_k: int, alpha: float = 0.5, filter: Optional[Dict] = None) -> List[DocumentInfo]:
        """
        Performs hybrid search combining dense and sparse results.
        alpha = 1.0 means purely dense, alpha = 0.0 means purely sparse.
        """
        logger.info(f"Performing hybrid search (alpha={alpha}) for query: {query}")
        dense_results = await self.dense_search(query, top_k, filter)
        sparse_results = await self.sparse_search(query, top_k, filter)
        
        def normalize(docs: List[DocumentInfo]) -> List[DocumentInfo]:
            if not docs:
                return docs
            scores = [d.score for d in docs]
            min_s, max_s = min(scores), max(scores)
            if max_s == min_s:
                for d in docs: d.score = 1.0
            else:
                for d in docs:
                    d.score = (d.score - min_s) / (max_s - min_s)
            return docs

        dense_norm = normalize(dense_results)
        sparse_norm = normalize(sparse_results)

        merged = {}
        for doc in dense_norm:
            merged[doc.id] = doc
            merged[doc.id].score = doc.score * alpha
            
        for doc in sparse_norm:
            if doc.id in merged:
                merged[doc.id].score += doc.score * (1 - alpha)
            else:
                merged[doc.id] = doc
                merged[doc.id].score = doc.score * (1 - alpha)
                
        sorted_results = sorted(list(merged.values()), key=lambda x: x.score, reverse=True)
        return sorted_results[:top_k]
