import logging
import asyncio
from typing import List, Dict, Any, Optional
from ..vector_store import VectorStore

logger = logging.getLogger(__name__)

class ChromaStore(VectorStore):
    """Chroma implementation of the VectorStore interface using AsyncClient."""
    
    def __init__(
        self, 
        persist_directory: Optional[str] = None, 
        host: Optional[str] = None, 
        port: Optional[int] = None,
        max_retries: int = 3,
        base_backoff: float = 1.0
    ):
        """Initialize the Chroma store.
        
        Args:
            persist_directory: Local directory for Chroma DB storage.
            host: Chroma server host (for client-server mode).
            port: Chroma server port.
            max_retries: Max retries for operations.
            base_backoff: Base backoff time for retries.
        """
        import chromadb
        
        self.persist_directory = persist_directory
        self.host = host
        self.port = port
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        
        if host and port:
            self.client = chromadb.AsyncHttpClient(host=host, port=port)
        elif persist_directory:
            # Persistent client in chroma is synchronous in core, but HttpClient is async.
            # We assume HttpClient since the prompt asks for async chromadb.
            self.client = chromadb.AsyncHttpClient(host="localhost", port=8000)
            logger.warning("persist_directory not fully supported in pure async Chroma. Using AsyncHttpClient instead.")
        else:
            self.client = chromadb.AsyncHttpClient(host="localhost", port=8000)

    async def _execute_with_retry(self, operation, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Chroma operation failed after {self.max_retries} attempts: {e}")
                    raise
                wait_time = self.base_backoff * (2 ** attempt)
                logger.warning(f"Chroma database operation failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

    async def _get_collection(self, collection_name: str):
        return await self.client.get_or_create_collection(name=collection_name)

    async def add(self, embeddings: List[Dict[str, Any]], collection_name: str) -> None:
        """Add embeddings to Chroma."""
        if not embeddings:
            return

        logger.info(f"Adding {len(embeddings)} embeddings to Chroma collection '{collection_name}'")
        
        async def _do_add():
            collection = await self._get_collection(collection_name)
            
            ids = [item["id"] for item in embeddings]
            embs = [item["embedding"] for item in embeddings]
            metadatas = [item.get("metadata", {}) or None for item in embeddings]
            documents = [item.get("metadata", {}).get("text", "") for item in embeddings]
            
            await collection.add(
                ids=ids,
                embeddings=embs,
                metadatas=metadatas,
                documents=documents
            )
            
        await self._execute_with_retry(_do_add)

    async def search(
        self, 
        query_vector: List[float], 
        collection_name: str, 
        top_k: int = 10, 
        filter_expr: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search Chroma for similar vectors."""
        logger.info(f"Searching Chroma collection '{collection_name}' for top {top_k} results")
        
        async def _do_search():
            collection = await self._get_collection(collection_name)
            
            # Simple where filter mapping
            where_filter = None
            if filter_expr:
                if len(filter_expr) == 1:
                    where_filter = dict(filter_expr)
                else:
                    where_filter = {"$and": [{k: v} for k, v in filter_expr.items()]}
            
            results = await collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                where=where_filter
            )
            
            # Formatting results
            formatted_results = []
            if results and results["ids"] and len(results["ids"]) > 0:
                for idx in range(len(results["ids"][0])):
                    formatted_results.append({
                        "id": results["ids"][0][idx],
                        "score": 1.0 - results["distances"][0][idx] if results["distances"] else 0.0,
                        "metadata": results["metadatas"][0][idx] if results["metadatas"] else {}
                    })
                    
            return formatted_results
            
        return await self._execute_with_retry(_do_search)

    async def delete(self, ids: List[str], collection_name: str) -> None:
        """Delete embeddings from Chroma by ID."""
        if not ids:
            return
            
        logger.info(f"Deleting {len(ids)} embeddings from Chroma collection '{collection_name}'")
        
        async def _do_delete():
            collection = await self._get_collection(collection_name)
            await collection.delete(ids=ids)
            
        await self._execute_with_retry(_do_delete)

    async def update(self, embeddings: List[Dict[str, Any]], collection_name: str) -> None:
        """Update existing embeddings in Chroma."""
        if not embeddings:
            return
            
        logger.info(f"Updating {len(embeddings)} embeddings in Chroma collection '{collection_name}'")
        
        async def _do_update():
            collection = await self._get_collection(collection_name)
            
            ids = [item["id"] for item in embeddings]
            embs = [item.get("embedding") for item in embeddings]
            metadatas = [item.get("metadata") for item in embeddings]
            documents = [item.get("metadata", {}).get("text", "") if item.get("metadata") else None for item in embeddings]
            
            # Chroma allows partial updates with `update` if the keys are passed, else they remain unchanged
            # Remove None values to avoid overriding existing data with Nones
            update_kwargs = {"ids": ids}
            if any(e is not None for e in embs):
                update_kwargs["embeddings"] = embs
            if any(m is not None for m in metadatas):
                update_kwargs["metadatas"] = metadatas
            if any(d is not None for d in documents):
                update_kwargs["documents"] = documents
                
            await collection.update(**update_kwargs)
            
        await self._execute_with_retry(_do_update)

    async def get(self, ids: List[str], collection_name: str) -> List[Dict[str, Any]]:
        """Retrieve embeddings by ID from Chroma."""
        if not ids:
            return []
            
        logger.info(f"Retrieving {len(ids)} embeddings from Chroma collection '{collection_name}'")
        
        async def _do_get():
            collection = await self._get_collection(collection_name)
            results = await collection.get(ids=ids)
            
            formatted_results = []
            if results and results["ids"]:
                for idx, record_id in enumerate(results["ids"]):
                    formatted_results.append({
                        "id": record_id,
                        "metadata": results["metadatas"][idx] if results["metadatas"] else {}
                    })
                    
            return formatted_results
            
        return await self._execute_with_retry(_do_get)

    async def health(self) -> bool:
        """Check the health of the Chroma connection."""
        try:
            async def _do_health():
                await self.client.heartbeat()
                return True
            return await self._execute_with_retry(_do_health)
        except Exception as e:
            logger.error(f"Chroma health check failed: {e}")
            return False
