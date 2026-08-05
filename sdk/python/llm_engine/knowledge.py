from typing import List, Dict, Any, Optional, Iterator, AsyncIterator
import httpx
from .exceptions import APIError
from .streaming import stream_sse_responses

class KnowledgeClient:
    def __init__(self, client: httpx.Client):
        self._client = client

    def create(self, name: str, description: str = "") -> dict:
        res = self._client.post("/v1/knowledge/create", json={"name": name, "description": description})
        res.raise_for_status()
        return res.json()

    def list(self) -> dict:
        res = self._client.get("/v1/knowledge/list")
        res.raise_for_status()
        return res.json()

    def upload(self, index_id: str, file_path: str, chunk_generator=None) -> dict:
        if chunk_generator:
            res = self._client.post(f"/v1/knowledge/upload", params={"index_id": index_id}, content=chunk_generator, headers={"Content-Type": "application/octet-stream"})
        else:
            with open(file_path, "rb") as f:
                res = self._client.post(f"/v1/knowledge/upload", params={"index_id": index_id}, content=f, headers={"Content-Type": "application/octet-stream"})
        res.raise_for_status()
        return res.json()

    def search(self, index_id: str, query: str, k: int = 5) -> dict:
        res = self._client.post("/v1/knowledge/search", json={"index_id": index_id, "query": query, "k": k})
        res.raise_for_status()
        return res.json()

    def retrieve(self, document_id: str) -> dict:
        res = self._client.get(f"/v1/knowledge/retrieve/{document_id}")
        res.raise_for_status()
        return res.json()

    def delete(self, resource_type: str, resource_id: str) -> dict:
        res = self._client.delete(f"/v1/knowledge/delete/{resource_type}/{resource_id}")
        res.raise_for_status()
        return res.json()

    def reindex(self, index_id: str) -> Iterator[dict]:
        with self._client.stream("POST", "/v1/knowledge/reindex", json={"index_id": index_id}) as response:
            for line in response.iter_lines():
                if line:
                    import json
                    yield json.loads(line)

    def citations(self, query: str, index_id: str) -> dict:
        res = self._client.post("/v1/knowledge/citations", json={"query": query, "index_id": index_id})
        res.raise_for_status()
        return res.json()

    def jobs(self) -> dict:
        res = self._client.get("/v1/knowledge/jobs")
        res.raise_for_status()
        return res.json()

    def status(self, job_id: str) -> dict:
        res = self._client.get(f"/v1/knowledge/status/{job_id}")
        res.raise_for_status()
        return res.json()


class AsyncKnowledgeClient:
    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    async def create(self, name: str, description: str = "") -> dict:
        res = await self._client.post("/v1/knowledge/create", json={"name": name, "description": description})
        res.raise_for_status()
        return res.json()

    async def list(self) -> dict:
        res = await self._client.get("/v1/knowledge/list")
        res.raise_for_status()
        return res.json()

    async def upload(self, index_id: str, file_path: str, chunk_generator=None) -> dict:
        if chunk_generator:
            res = await self._client.post(f"/v1/knowledge/upload", params={"index_id": index_id}, content=chunk_generator, headers={"Content-Type": "application/octet-stream"})
        else:
            with open(file_path, "rb") as f:
                res = await self._client.post(f"/v1/knowledge/upload", params={"index_id": index_id}, content=f.read(), headers={"Content-Type": "application/octet-stream"})
        res.raise_for_status()
        return res.json()

    async def search(self, index_id: str, query: str, k: int = 5) -> dict:
        res = await self._client.post("/v1/knowledge/search", json={"index_id": index_id, "query": query, "k": k})
        res.raise_for_status()
        return res.json()

    async def retrieve(self, document_id: str) -> dict:
        res = await self._client.get(f"/v1/knowledge/retrieve/{document_id}")
        res.raise_for_status()
        return res.json()

    async def delete(self, resource_type: str, resource_id: str) -> dict:
        res = await self._client.delete(f"/v1/knowledge/delete/{resource_type}/{resource_id}")
        res.raise_for_status()
        return res.json()

    async def reindex(self, index_id: str) -> AsyncIterator[dict]:
        async with self._client.stream("POST", "/v1/knowledge/reindex", json={"index_id": index_id}) as response:
            async for line in response.aiter_lines():
                if line:
                    import json
                    yield json.loads(line)

    async def citations(self, query: str, index_id: str) -> dict:
        res = await self._client.post("/v1/knowledge/citations", json={"query": query, "index_id": index_id})
        res.raise_for_status()
        return res.json()

    async def jobs(self) -> dict:
        res = await self._client.get("/v1/knowledge/jobs")
        res.raise_for_status()
        return res.json()

    async def status(self, job_id: str) -> dict:
        res = await self._client.get(f"/v1/knowledge/status/{job_id}")
        res.raise_for_status()
        return res.json()
