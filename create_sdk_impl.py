import os
import re

PROJECT_ROOT = r"c:\Users\Yogesh E\OneDrive\Desktop\Manjus\llm-inference-engine"

def write_file(rel_path, content):
    full_path = os.path.join(PROJECT_ROOT, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

# --- 1. PYTHON SDK ---

write_file("sdk/python/llm_engine/knowledge.py", """
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

    async def jobs(self) -> dict:
        res = await self._client.get("/v1/knowledge/jobs")
        res.raise_for_status()
        return res.json()

    async def status(self, job_id: str) -> dict:
        res = await self._client.get(f"/v1/knowledge/status/{job_id}")
        res.raise_for_status()
        return res.json()
""")

# update python client.py
client_file = os.path.join(PROJECT_ROOT, "sdk/python/llm_engine/client.py")
if os.path.exists(client_file):
    with open(client_file, "r") as f:
        client_code = f.read()
    if "from .knowledge import KnowledgeClient, AsyncKnowledgeClient" not in client_code:
        client_code = "from .knowledge import KnowledgeClient, AsyncKnowledgeClient\n" + client_code
        client_code = client_code.replace("self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=self.timeout)", "self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=self.timeout)\n        self.knowledge = KnowledgeClient(self.client)")
        client_code = client_code.replace("self.client = httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=self.timeout)", "self.client = httpx.AsyncClient(base_url=self.base_url, headers=headers, timeout=self.timeout)\n        self.knowledge = AsyncKnowledgeClient(self.client)")
        with open(client_file, "w") as f:
            f.write(client_code)


# --- 2. TYPESCRIPT SDK ---
write_file("sdk/typescript/src/knowledge.ts", """
export class KnowledgeClient {
  private _fetch: (url: string, options: any) => Promise<Response>;
  private _baseUrl: string;
  private _headers: Record<string, string>;

  constructor(fetchImpl: (url: string, options: any) => Promise<Response>, baseUrl: string, headers: Record<string, string>) {
    this._fetch = fetchImpl;
    this._baseUrl = baseUrl;
    this._headers = headers;
  }

  private async request(method: string, path: string, body?: any, isStream = false) {
    const res = await this._fetch(`${this._baseUrl}${path}`, {
      method,
      headers: this._headers,
      body: body ? JSON.stringify(body) : undefined,
    });
    if (!res.ok) throw new Error(`API Error ${res.status}`);
    return isStream ? res : res.json();
  }

  async create(name: string, description: string = '') {
    return this.request('POST', '/v1/knowledge/create', { name, description });
  }

  async list() {
    return this.request('GET', '/v1/knowledge/list');
  }

  async search(indexId: string, query: string, k: number = 5) {
    return this.request('POST', '/v1/knowledge/search', { index_id: indexId, query, k });
  }

  async retrieve(documentId: string) {
    return this.request('GET', `/v1/knowledge/retrieve/${documentId}`);
  }

  async delete(resourceType: 'index'|'document', id: string) {
    return this.request('DELETE', `/v1/knowledge/delete/${resourceType}/${id}`);
  }

  async reindex(indexId: string) {
    return this.request('POST', '/v1/knowledge/reindex', { index_id: indexId }, true);
  }

  async jobs() {
    return this.request('GET', '/v1/knowledge/jobs');
  }

  async status(jobId: string) {
    return this.request('GET', `/v1/knowledge/status/${jobId}`);
  }
}
""")

ts_client_file = os.path.join(PROJECT_ROOT, "sdk/typescript/src/client.ts")
if os.path.exists(ts_client_file):
    with open(ts_client_file, "r") as f:
        ts_client_code = f.read()
    if "KnowledgeClient" not in ts_client_code:
        ts_client_code = "import { KnowledgeClient } from './knowledge.js';\n" + ts_client_code
        ts_client_code = ts_client_code.replace("export class LLMEngineClient {", "export class LLMEngineClient {\n  public knowledge: KnowledgeClient;")
        ts_client_code = ts_client_code.replace("this.headers['X-Organization-ID'] = config.organizationId;\n    }", "this.headers['X-Organization-ID'] = config.organizationId;\n    }\n    this.knowledge = new KnowledgeClient(fetch, this.baseUrl, this.headers);")
        with open(ts_client_file, "w") as f:
            f.write(ts_client_code)

print("SDK scripts written successfully.")
