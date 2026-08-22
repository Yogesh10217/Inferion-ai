"""Python SDK Client for Marketplace Platform."""

from typing import Dict, Any, List, Optional
import httpx


class MarketplaceClient:
    """Python SDK client for Enterprise AI Marketplace."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=timeout)

    def create_item(self, title: str, summary: str, category: str, publisher_id: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
        resp = self.client.post("/v1/marketplace/items", json={"title": title, "summary": summary, "category": category, "publisher_id": publisher_id, "manifest": manifest})
        resp.raise_for_status()
        return resp.json()

    def list_items(self, category: Optional[str] = None) -> Dict[str, Any]:
        params = {"category": category} if category else {}
        resp = self.client.get("/v1/marketplace/items", params=params)
        resp.raise_for_status()
        return resp.json()

    def submit_item(self, item_id: str) -> Dict[str, Any]:
        resp = self.client.post(f"/v1/marketplace/items/{item_id}/submit")
        resp.raise_for_status()
        return resp.json()

    def publish_item(self, item_id: str) -> Dict[str, Any]:
        resp = self.client.post(f"/v1/marketplace/items/{item_id}/publish")
        resp.raise_for_status()
        return resp.json()

    def install_item(self, item_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.post(f"/v1/marketplace/items/{item_id}/install", json={"tenant_id": tenant_id})
        resp.raise_for_status()
        return resp.json()
