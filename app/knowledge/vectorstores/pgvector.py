import logging
import asyncio
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text, inspect
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from ..vector_store import VectorStore
import json

logger = logging.getLogger(__name__)

class PGVectorStore(VectorStore):
    """PGVector implementation of the VectorStore interface using async SQLAlchemy."""
    
    def __init__(
        self, 
        connection_string: str, 
        pool_size: int = 10, 
        max_overflow: int = 20,
        max_retries: int = 3,
        base_backoff: float = 1.0
    ):
        """Initialize the PGVector store with connection pooling and retries.
        
        Args:
            connection_string: PostgreSQL connection string (asyncpg).
            pool_size: Connection pool size.
            max_overflow: Max overflow for connection pool.
            max_retries: Max retries for operations.
            base_backoff: Base backoff time for retries in seconds.
        """
        connect_args = {}
        if "postgresql+asyncpg" in connection_string or "postgres+asyncpg" in connection_string:
            if "?" in connection_string:
                base_url, query_str = connection_string.split("?", 1)
                params = [p for p in query_str.split("&") if not p.startswith("sslmode=") and not p.startswith("channel_binding=")]
                connection_string = base_url + ("?" + "&".join(params) if params else "")
            import ssl
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE
            connect_args["ssl"] = ssl_ctx

        self.engine = create_async_engine(
            connection_string,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            connect_args=connect_args
        )
        self.session_maker = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        
    async def _execute_with_retry(self, operation, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return await operation(*args, **kwargs)
            except OperationalError as e:
                if attempt == self.max_retries - 1:
                    logger.error(f"Operation failed after {self.max_retries} attempts: {e}")
                    raise
                wait_time = self.base_backoff * (2 ** attempt)
                logger.warning(f"Database operation failed: {e}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            except SQLAlchemyError as e:
                logger.error(f"SQLAlchemy error during operation: {e}")
                raise

    async def _ensure_collection_table(self, session: AsyncSession, collection_name: str, dim: int):
        # Namespace isolation achieved by creating a separate table per collection
        # Or a single table with collection_name column. Let's use a single table with collection name
        create_extension_sql = text("CREATE EXTENSION IF NOT EXISTS vector;")
        await session.execute(create_extension_sql)
        
        create_table_sql = text(f"""
            CREATE TABLE IF NOT EXISTS document_embeddings (
                id VARCHAR(255) PRIMARY KEY,
                collection_name VARCHAR(255) NOT NULL,
                embedding vector({dim}),
                metadata JSONB
            );
        """)
        await session.execute(create_table_sql)
        
        create_index_sql = text(f"""
            CREATE INDEX IF NOT EXISTS idx_collection_name ON document_embeddings (collection_name);
        """)
        await session.execute(create_index_sql)
        await session.commit()

    async def add(self, embeddings: List[Dict[str, Any]], collection_name: str) -> None:
        """Add embeddings to the PGVector store in batches."""
        if not embeddings:
            return

        logger.info(f"Adding {len(embeddings)} embeddings to PGVector collection '{collection_name}'")
        dim = len(embeddings[0].get("embedding", []))
        
        async def _do_add():
            async with self.session_maker() as session:
                await self._ensure_collection_table(session, collection_name, dim)
                
                # Batch insert
                insert_sql = text("""
                    INSERT INTO document_embeddings (id, collection_name, embedding, metadata)
                    VALUES (:id, :collection_name, :embedding, :metadata)
                    ON CONFLICT (id) DO UPDATE SET
                    embedding = EXCLUDED.embedding,
                    metadata = EXCLUDED.metadata,
                    collection_name = EXCLUDED.collection_name
                """)
                
                params = []
                for item in embeddings:
                    # PGVector expects string representation for vector like '[1.0, 2.0, ...]'
                    vector_str = "[" + ",".join(map(str, item["embedding"])) + "]"
                    params.append({
                        "id": item["id"],
                        "collection_name": collection_name,
                        "embedding": vector_str,
                        "metadata": json.dumps(item.get("metadata", {}))
                    })
                
                # Execute in chunks if necessary, here we do it all at once
                await session.execute(insert_sql, params)
                await session.commit()
                
        await self._execute_with_retry(_do_add)

    async def search(
        self, 
        query_vector: List[float], 
        collection_name: str, 
        top_k: int = 10, 
        filter_expr: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Search the PGVector store for similar vectors with metadata filtering."""
        logger.info(f"Searching PGVector collection '{collection_name}' for top {top_k} results")
        
        async def _do_search():
            async with self.session_maker() as session:
                vector_str = "[" + ",".join(map(str, query_vector)) + "]"
                
                base_query = """
                    SELECT id, metadata, embedding <=> :query_vector AS distance
                    FROM document_embeddings
                    WHERE collection_name = :collection_name
                """
                
                # Metadata filtering (simple JSONB containment for now)
                if filter_expr:
                    base_query += " AND metadata @> :filter_expr"
                    
                base_query += " ORDER BY distance ASC LIMIT :top_k"
                
                sql = text(base_query)
                params = {
                    "query_vector": vector_str,
                    "collection_name": collection_name,
                    "top_k": top_k
                }
                
                if filter_expr:
                    params["filter_expr"] = json.dumps(filter_expr)
                    
                result = await session.execute(sql, params)
                rows = result.fetchall()
                
                return [
                    {
                        "id": row.id,
                        "metadata": row.metadata,
                        "score": 1.0 - row.distance # converting distance to similarity score
                    }
                    for row in rows
                ]
                
        return await self._execute_with_retry(_do_search)

    async def delete(self, ids: List[str], collection_name: str) -> None:
        """Delete embeddings from the PGVector store by ID in batches."""
        if not ids:
            return
            
        logger.info(f"Deleting {len(ids)} embeddings from PGVector collection '{collection_name}'")
        
        async def _do_delete():
            async with self.session_maker() as session:
                sql = text("""
                    DELETE FROM document_embeddings 
                    WHERE id = ANY(:ids) AND collection_name = :collection_name
                """)
                await session.execute(sql, {"ids": ids, "collection_name": collection_name})
                await session.commit()
                
        await self._execute_with_retry(_do_delete)

    async def update(self, embeddings: List[Dict[str, Any]], collection_name: str) -> None:
        """Partial update of existing embeddings/metadata in the PGVector store."""
        if not embeddings:
            return
            
        logger.info(f"Updating {len(embeddings)} embeddings in PGVector collection '{collection_name}'")
        
        async def _do_update():
            async with self.session_maker() as session:
                for item in embeddings:
                    updates = []
                    params = {"id": item["id"], "collection_name": collection_name}
                    
                    if "embedding" in item:
                        updates.append("embedding = :embedding")
                        params["embedding"] = "[" + ",".join(map(str, item["embedding"])) + "]"
                        
                    if "metadata" in item:
                        # For partial update, we could merge JSONB, but we will replace for simplicity here,
                        # or we can use JSONB concatenation
                        updates.append("metadata = metadata || :metadata")
                        params["metadata"] = json.dumps(item["metadata"])
                        
                    if not updates:
                        continue
                        
                    set_clause = ", ".join(updates)
                    sql = text(f"""
                        UPDATE document_embeddings 
                        SET {set_clause}
                        WHERE id = :id AND collection_name = :collection_name
                    """)
                    await session.execute(sql, params)
                    
                await session.commit()
                
        await self._execute_with_retry(_do_update)

    async def get(self, ids: List[str], collection_name: str) -> List[Dict[str, Any]]:
        """Retrieve embeddings by ID from PGVector."""
        if not ids:
            return []
            
        logger.info(f"Retrieving {len(ids)} embeddings from PGVector collection '{collection_name}'")
        
        async def _do_get():
            async with self.session_maker() as session:
                sql = text("""
                    SELECT id, metadata
                    FROM document_embeddings
                    WHERE id = ANY(:ids) AND collection_name = :collection_name
                """)
                result = await session.execute(sql, {"ids": ids, "collection_name": collection_name})
                rows = result.fetchall()
                
                return [{"id": row.id, "metadata": row.metadata} for row in rows]
                
        return await self._execute_with_retry(_do_get)

    async def health(self) -> bool:
        """Check the health of the PGVector connection."""
        try:
            async def _do_health():
                async with self.session_maker() as session:
                    await session.execute(text("SELECT 1"))
                    return True
            return await self._execute_with_retry(_do_health)
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
