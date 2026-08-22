"""Python SDK Client for Extension Framework."""

from typing import Dict, Any, List, Optional
import httpx


class ExtensionsClient:
    """Python SDK client for Extension Framework."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=timeout)

    def register_extension(self, manifest: Dict[str, Any], tenant_id: str = "global", developer_id: str = "system") -> Dict[str, Any]:
        resp = self.client.post("/v1/extensions", json={"manifest": manifest, "tenant_id": tenant_id, "developer_id": developer_id})
        resp.raise_for_status()
        return resp.json()

    def list_extensions(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"tenant_id": tenant_id} if tenant_id else {}
        resp = self.client.get("/v1/extensions", params=params)
        resp.raise_for_status()
        return resp.json()

    def enable_extension(self, extension_id: str) -> Dict[str, Any]:
        resp = self.client.post(f"/v1/extensions/{extension_id}/enable")
        resp.raise_for_status()
        return resp.json()

    def disable_extension(self, extension_id: str) -> Dict[str, Any]:
        resp = self.client.post(f"/v1/extensions/{extension_id}/disable")
        resp.raise_for_status()
        return resp.json()

    def rollback_extension(self, extension_id: str, target_version: str) -> Dict[str, Any]:
        resp = self.client.post(f"/v1/extensions/{extension_id}/rollback", json={"target_version": target_version})
        resp.raise_for_status()
        return resp.json()
