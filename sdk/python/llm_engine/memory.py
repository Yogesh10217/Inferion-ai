"""
Memory SDK Client Subsystem
"""

from typing import Dict, Any, List, Optional
import httpx


class MemoryClient:
    """Python SDK Client for Enterprise Memory Platform."""

    def __init__(self, client: httpx.Client, base_url: str):
        self._client = client
        self.base_url = base_url

    def create(self, content: str, context_hint: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {"content": content, "context_hint": context_hint, "user_id": user_id}
        resp = self._client.post(f"{self.base_url}/v1/memory", json=payload)
        resp.raise_for_status()
        return resp.json()

    def list(self, memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {"memory_type": memory_type} if memory_type else {}
        resp = self._client.get(f"{self.base_url}/v1/memory", params=params)
        resp.raise_for_status()
        return resp.json()

    def get(self, memory_id: str) -> Dict[str, Any]:
        resp = self._client.get(f"{self.base_url}/v1/memory/{memory_id}")
        resp.raise_for_status()
        return resp.json()

    def delete(self, memory_id: str) -> Dict[str, Any]:
        resp = self._client.delete(f"{self.base_url}/v1/memory/{memory_id}")
        resp.raise_for_status()
        return resp.json()

    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        payload = {"query": query, "top_k": top_k}
        resp = self._client.post(f"{self.base_url}/v1/memory/search", json=payload)
        resp.raise_for_status()
        return resp.json()

    def compress(self, session_id: str, max_tokens: int = 2048) -> Dict[str, Any]:
        payload = {"session_id": session_id, "max_tokens": max_tokens}
        resp = self._client.post(f"{self.base_url}/v1/memory/compress", json=payload)
        resp.raise_for_status()
        return resp.json()

    def summarize(self, text: str, max_words: int = 100) -> Dict[str, Any]:
        payload = {"text": text, "max_words": max_words}
        resp = self._client.post(f"{self.base_url}/v1/memory/summarize", json=payload)
        resp.raise_for_status()
        return resp.json()

    def archive(self, memory_id: str) -> Dict[str, Any]:
        resp = self._client.post(f"{self.base_url}/v1/memory/archive", params={"memory_id": memory_id})
        resp.raise_for_status()
        return resp.json()

    def analytics(self) -> Dict[str, Any]:
        resp = self._client.get(f"{self.base_url}/v1/memory/analytics")
        resp.raise_for_status()
        return resp.json()

    def get_profile(self, user_id: str = "default_user") -> Dict[str, Any]:
        resp = self._client.get(f"{self.base_url}/v1/memory/profile", params={"user_id": user_id})
        resp.raise_for_status()
        return resp.json()

    def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        payload = {"profile_data": profile_data}
        resp = self._client.patch(f"{self.base_url}/v1/memory/profile", params={"user_id": user_id}, json=payload)
        resp.raise_for_status()
        return resp.json()
