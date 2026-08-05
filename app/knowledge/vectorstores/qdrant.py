import logging
import asyncio
from typing import List, Dict, Any, Optional
from ..vector_store import VectorStore

logger = logging.getLogger(__name__)

class QdrantStore(VectorStore):
    """Qdrant implementation of the VectorStore interface."""
    
    def __init__(
        self, 
        url: str, 
        api_key: Optional[str] = None,
        max_retries: int = 3,
        base_backoff: float = 1.0,
        timeout: float = 10.0
    ):
        """Initialize the Qdrant store.
        
        Args:
            url: Qdrant server URL.
            api_key: Qdrant API key (optional).
            max_retries: Max retries for operations.
            base_backoff: Base backoff time for retries.
            timeout: Timeout for Qdrant client operations.
        """
        import qdrant_client
        from qdrant_client import AsyncQdrantClient
        
        self.url = url
        self.api_key = api_key
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.client = AsyncQdrantClient(
            url=url, 
            api_key=api_key, 
            timeout=timeout
        )
        # Connection pooling is handled internally by AsyncQdrantClient (which uses httpx client)

    async def _execute_with_retry(self, operation, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Qdrant operation failed after {self.max_retries} attempts: {e}")
                    raise
                wait_time = self.base_backoff * (2 ** attempt)
                logger.warning(f"Qdrant database operation failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

    async def _ensure_collection(self, collection_name: str, dim: int):
        from qdrant_client.http.models import VectorParams, Distance
        from qdrant_client.http.exceptions import UnexpectedResponse

        try:
            await self.client.get_collection(collection_name)
        except UnexpectedResponse as e:
            if e.status_code == 404:
                await self.client.create_collection(
                    collection_name=collection_name,
                    vectors_config=VectorParams(size=dim, distance=Distance.COSINE)
                )
            else:
                raise

    async def add(self, embeddings: List[Dict[str, Any]], collection_name: str) -> None:
        """Add embeddings to Qdrant."""
        if not embeddings:
            return

        logger.info(f"Adding {len(embeddings)} embeddings to Qdrant collection '{collection_name}'")
        from qdrant_client.http.models import PointStruct

        dim = len(embeddings[0].get("embedding", []))
        
        async def _do_add():
            await self._ensure_collection(collection_name, dim)
            
            points = []
            for item in embeddings:
                # Qdrant accepts UUID or unsigned integer as ID. If item["id"] is string, it must be UUID.
                # In real apps, map string ID to UUID if necessary.
                points.append(
                    PointStruct(
                        id=item["id"],
                        vector=item["embedding"],
                        payload=item.get("metadata", {})
                    )
                )
            # Batch upsert
            await self.client.upsert(
                collection_name=collection_name,
                points=points
            )
            
        await self._execute_with_retry(_do_add)

    async def search(
        self, 
        query_vector: List[float], 
        collection_name: str, 
        top_k: int = 10, 
        filter_expr: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search Qdrant for similar vectors."""
        logger.info(f"Searching Qdrant collection '{collection_name}' for top {top_k} results")
        from qdrant_client.http.models import Filter, FieldCondition, MatchValue

        # Simple metadata filtering mapping from dict to Qdrant Filter
        query_filter = None
        if filter_expr:
            must_conditions = []
            for key, value in filter_expr.items():
                must_conditions.append(
                    FieldCondition(
                        key=key,
                        match=MatchValue(value=value)
                    )
                )
            query_filter = Filter(must=must_conditions)

        async def _do_search():
            results = await self.client.search(
                collection_name=collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=top_k,
                with_payload=True
            )
            
            return [
                {
                    "id": str(res.id),
                    "score": res.score,
                    "metadata": res.payload
                }
                for res in results
            ]
            
        return await self._execute_with_retry(_do_search)

    async def delete(self, ids: List[str], collection_name: str) -> None:
        """Delete embeddings from Qdrant by ID."""
        if not ids:
            return
            
        logger.info(f"Deleting {len(ids)} embeddings from Qdrant collection '{collection_name}'")
        from qdrant_client.http.models import PointIdsList
        
        async def _do_delete():
            await self.client.delete(
                collection_name=collection_name,
                points_selector=PointIdsList(points=ids)
            )
            
        await self._execute_with_retry(_do_delete)

    async def update(self, embeddings: List[Dict[str, Any]], collection_name: str) -> None:
        """Partial update existing embeddings and metadata in Qdrant."""
        if not embeddings:
            return
            
        logger.info(f"Updating {len(embeddings)} embeddings in Qdrant collection '{collection_name}'")
        from qdrant_client.http.models import PointStruct, PointVectors
        
        async def _do_update():
            # Qdrant supports separate payload update and vector update or full upsert
            # We'll check what is provided and perform accordingly.
            points_to_upsert = []
            for item in embeddings:
                # If both embedding and metadata are given, we can just upsert
                if "embedding" in item and "metadata" in item:
                    points_to_upsert.append(
                        PointStruct(
                            id=item["id"],
                            vector=item["embedding"],
                            payload=item["metadata"]
                        )
                    )
                elif "metadata" in item:
                    await self.client.set_payload(
                        collection_name=collection_name,
                        payload=item["metadata"],
                        points=[item["id"]]
                    )
                elif "embedding" in item:
                    await self.client.update_vectors(
                        collection_name=collection_name,
                        points=[
                            PointVectors(
                                id=item["id"],
                                vector=item["embedding"]
                            )
                        ]
                    )
            
            if points_to_upsert:
                await self.client.upsert(
                    collection_name=collection_name,
                    points=points_to_upsert
                )
                
        await self._execute_with_retry(_do_update)

    async def get(self, ids: List[str], collection_name: str) -> List[Dict[str, Any]]:
        """Retrieve embeddings by ID from Qdrant."""
        if not ids:
            return []
            
        logger.info(f"Retrieving {len(ids)} embeddings from Qdrant collection '{collection_name}'")
        
        async def _do_get():
            records = await self.client.retrieve(
                collection_name=collection_name,
                ids=ids,
                with_payload=True,
                with_vectors=False
            )
            return [
                {
                    "id": str(record.id),
                    "metadata": record.payload
                }
                for record in records
            ]
            
        return await self._execute_with_retry(_do_get)

    async def health(self) -> bool:
        """Check the health of the Qdrant connection."""
        try:
            async def _do_health():
                collections = await self.client.get_collections()
                return True
            return await self._execute_with_retry(_do_health)
        except Exception as e:
            logger.error(f"Qdrant health check failed: {e}")
            return False
