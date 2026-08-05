import asyncio
import hashlib
import logging
from typing import List, Protocol, Dict, Optional, Any
from app.knowledge.pipeline import PipelineStage, DocumentContext

logger = logging.getLogger(__name__)

class ProviderFactory(Protocol):
    """Protocol for embedding providers."""
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        ...

class OpenAIProvider:
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        import openai
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.model = model

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        response = await self.client.embeddings.create(input=texts, model=self.model)
        return [data.embedding for data in response.data]

class OllamaProvider:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama2"):
        import httpx
        self.base_url = base_url
        self.model = model
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        embeddings = []
        for text in texts:
            response = await self.client.post("/api/embeddings", json={"model": self.model, "prompt": text})
            response.raise_for_status()
            embeddings.append(response.json()["embedding"])
        return embeddings

class CohereProvider:
    def __init__(self, api_key: str, model: str = "embed-english-v3.0"):
        import cohere
        self.client = cohere.AsyncClient(api_key=api_key)
        self.model = model

    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        response = await self.client.embed(texts=texts, model=self.model, input_type="search_document")
        return response.embeddings

class EmbeddingCache:
    def __init__(self):
        self.cache: Dict[str, List[float]] = {}
    
    def get(self, text: str) -> Optional[List[float]]:
        key = hashlib.sha256(text.encode()).hexdigest()
        return self.cache.get(key)
    
    def set(self, text: str, embedding: List[float]):
        key = hashlib.sha256(text.encode()).hexdigest()
        self.cache[key] = embedding

class EmbeddingStage(PipelineStage):
    """Generates embeddings for chunks using a ProviderFactory with batching, retries, and caching."""
    
    def __init__(self, provider_factory: ProviderFactory, batch_size: int = 10, max_retries: int = 3, base_backoff: float = 1.0, rate_limit_delay: float = 0.1):
        self.provider_factory = provider_factory
        self.batch_size = batch_size
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.rate_limit_delay = rate_limit_delay
        self.cache = EmbeddingCache()

    async def _get_embeddings_with_retry(self, texts: List[str]) -> List[List[float]]:
        from app.monitoring.metrics import knowledge_embedding_latency_seconds
        import time
        start_time = time.time()
        try:
            for attempt in range(self.max_retries):
                try:
                    # Rate limiting delay
                    if self.rate_limit_delay > 0:
                        await asyncio.sleep(self.rate_limit_delay)
                    return await self.provider_factory.get_embeddings(texts)
                except Exception as e:
                    if attempt == self.max_retries - 1:
                        logger.error(f"Failed to get embeddings after {self.max_retries} attempts: {e}")
                        raise
                    wait_time = self.base_backoff * (2 ** attempt)
                    logger.warning(f"Embedding generation failed: {e}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
            return []
        finally:
            knowledge_embedding_latency_seconds.observe(time.time() - start_time)

    async def process(self, context: DocumentContext) -> DocumentContext:
        """Generates embeddings for all document chunks."""
        if not context.chunks:
            context.errors.append("No chunks available for embedding.")
            return context

        # Deduplication and caching logic
        unique_texts = []
        text_to_idx = {}
        for idx, chunk in enumerate(context.chunks):
            text = chunk["text"]
            if text not in text_to_idx:
                text_to_idx[text] = []
                unique_texts.append(text)
            text_to_idx[text].append(idx)

        all_embeddings = [None] * len(context.chunks)
        texts_to_embed = []
        texts_to_embed_indices = []

        from app.monitoring.metrics import knowledge_cache_hits_total, knowledge_cache_misses_total, embedding_tokens_total
        from app.billing.tracker import tracker
        
        cache_hits = 0
        cache_misses = 0
        tokens_to_embed = 0

        for text in unique_texts:
            cached_emb = self.cache.get(text)
            if cached_emb:
                cache_hits += 1
                for idx in text_to_idx[text]:
                    all_embeddings[idx] = cached_emb
            else:
                cache_misses += 1
                texts_to_embed.append(text)
                texts_to_embed_indices.append(text_to_idx[text])
                
                # Retrieve token count from the first chunk that has this text
                first_idx = text_to_idx[text][0]
                token_count = context.chunks[first_idx].get("token_count", len(text) // 4)
                tokens_to_embed += token_count

        knowledge_cache_hits_total.inc(cache_hits)
        knowledge_cache_misses_total.inc(cache_misses)
        
        if tokens_to_embed > 0:
            embedding_tokens_total.inc(tokens_to_embed)
            tracker.track_embedding_tokens(tokens_to_embed)

        # Batching logic for missing embeddings
        for i in range(0, len(texts_to_embed), self.batch_size):
            batch = texts_to_embed[i:i+self.batch_size]
            batch_indices = texts_to_embed_indices[i:i+self.batch_size]
            try:
                batch_embeddings = await self._get_embeddings_with_retry(batch)
                for text, indices, emb in zip(batch, batch_indices, batch_embeddings):
                    self.cache.set(text, emb)
                    for idx in indices:
                        all_embeddings[idx] = emb
            except Exception as e:
                context.errors.append(f"Failed to generate embeddings for batch {i//self.batch_size}: {e}")
                return context
                
        context.embeddings = all_embeddings
        
        # Assign embeddings back to chunks
        for chunk, embedding in zip(context.chunks, context.embeddings):
            chunk["embedding"] = embedding
            
        return context
