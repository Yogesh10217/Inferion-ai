"""
Reranker Module.
Provider abstraction for reranking search results.
"""
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import logging
import asyncio
import httpx
try:
    from sentence_transformers import CrossEncoder
except ImportError:
    CrossEncoder = None

logger = logging.getLogger(__name__)

class DocumentInfo:
    def __init__(self, id: str, text: str, metadata: Dict[str, Any], score: float = 0.0):
        self.id = id
        self.text = text
        self.metadata = metadata
        self.score = score

class BaseReranker(ABC):
    """Abstract base class for rerankers."""
    
    async def rerank(self, query: str, documents: List[DocumentInfo], top_n: int) -> List[DocumentInfo]:
        """Reranks a list of documents based on the query."""
        from app.monitoring.metrics import knowledge_rerank_latency_seconds, reranking_requests_total, knowledge_errors_total
        from app.billing.tracker import tracker
        import time
        
        start_time = time.time()
        reranking_requests_total.inc()
        tracker.track_reranking_request()
        
        try:
            results = await self._do_rerank(query, documents, top_n)
        except Exception:
            knowledge_errors_total.inc()
            raise
        finally:
            knowledge_rerank_latency_seconds.observe(time.time() - start_time)
            
        return results

    @abstractmethod
    async def _do_rerank(self, query: str, documents: List[DocumentInfo], top_n: int) -> List[DocumentInfo]:
        """Internal rerank method to be implemented by subclasses."""
        pass

class CohereReranker(BaseReranker):
    """Cohere Reranker implementation."""
    def __init__(self, api_key: str, model: str = "rerank-english-v2.0"):
        self.api_key = api_key
        self.model = model
        
    async def _do_rerank(self, query: str, documents: List[DocumentInfo], top_n: int) -> List[DocumentInfo]:
        if not documents:
            return []
            
        logger.info(f"Reranking {len(documents)} documents using Cohere ({self.model})")
        texts = [doc.text for doc in documents]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.cohere.ai/v1/rerank",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "query": query,
                    "documents": texts,
                    "model": self.model,
                    "top_n": top_n
                },
                timeout=15.0
            )
            response.raise_for_status()
            data = response.json()
            
        results = data.get("results", [])
        reranked_docs = []
        for res in results:
            idx = res["index"]
            score = res["relevance_score"]
            doc = documents[idx]
            doc.score = score
            reranked_docs.append(doc)
            
        return reranked_docs

class CrossEncoderReranker(BaseReranker):
    """Local CrossEncoder Reranker implementation (e.g. for BGE or MS-MARCO)."""
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model_name = model_name
        if CrossEncoder is None:
            raise ImportError("sentence_transformers is not installed. Please install it to use CrossEncoderReranker.")
        self.model = CrossEncoder(self.model_name)
        
    async def _do_rerank(self, query: str, documents: List[DocumentInfo], top_n: int) -> List[DocumentInfo]:
        if not documents:
            return []
            
        logger.info(f"Reranking {len(documents)} documents using CrossEncoder ({self.model_name})")
        # Run synchronous model in thread pool
        pairs = [[query, doc.text] for doc in documents]
        scores = await asyncio.to_thread(self.model.predict, pairs)
        
        for doc, score in zip(documents, scores):
            doc.score = float(score)
            
        sorted_docs = sorted(documents, key=lambda x: x.score, reverse=True)
        return sorted_docs[:top_n]

class BGEReranker(CrossEncoderReranker):
    """BGE Reranker implementation."""
    def __init__(self, model_name: str = "BAAI/bge-reranker-base"):
        super().__init__(model_name=model_name)

class JinaReranker(BaseReranker):
    """Jina Reranker implementation."""
    def __init__(self, api_key: str, model: str = "jina-reranker-v1-base-en"):
        self.api_key = api_key
        self.model = model
        
    async def _do_rerank(self, query: str, documents: List[DocumentInfo], top_n: int) -> List[DocumentInfo]:
        if not documents:
            return []
            
        logger.info(f"Reranking {len(documents)} documents using Jina ({self.model})")
        texts = [doc.text for doc in documents]
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.jina.ai/v1/rerank",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "query": query,
                    "documents": texts,
                    "model": self.model,
                    "top_n": top_n
                },
                timeout=15.0
            )
            response.raise_for_status()
            data = response.json()
            
        results = data.get("results", [])
        reranked_docs = []
        for res in results:
            idx = res["index"]
            score = res["relevance_score"]
            doc = documents[idx]
            doc.score = score
            reranked_docs.append(doc)
            
        return reranked_docs[:top_n]
