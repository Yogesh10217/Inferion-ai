import pytest
import sqlite3
import tempfile
import os

@pytest.fixture
def sqlite_db():
    fd, path = tempfile.mkstemp()
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE metadata (id TEXT PRIMARY KEY, info TEXT)")
    yield conn
    conn.close()
    os.close(fd)
    os.remove(path)

@pytest.fixture
def real_vector_store():
    # In-memory implementation of VectorStore for testing (acting as local vector store)
    from app.knowledge.vector_store import VectorStore
    class LocalSQLiteVectorStore(VectorStore):
        def __init__(self):
            self.data = {}
        async def add(self, embeddings, collection_name):
            for e in embeddings:
                self.data[e['id']] = e
        async def search(self, query_vector, collection_name, top_k=10, filter_expr=None):
            return list(self.data.values())[:top_k]
        async def delete(self, ids, collection_name):
            for i in ids:
                self.data.pop(i, None)
        async def update(self, embeddings, collection_name):
            await self.add(embeddings, collection_name)
        async def get(self, ids, collection_name):
            return [self.data[i] for i in ids if i in self.data]
        async def health(self):
            return True
    return LocalSQLiteVectorStore()
