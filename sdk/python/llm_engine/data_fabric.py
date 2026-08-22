"""Python SDK Client for Data Fabric API."""

from typing import Dict, Any, List, Optional
import httpx


class DataFabricClient:
    """Python SDK client for Data Sources, Synchronization, Data Catalog, and Governance."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=timeout)

    def create_data_source(self, name: str, source_type: str, connector_type: str, tenant_id: str = "global", configuration: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        resp = self.client.post("/v1/data-sources", json={"name": name, "source_type": source_type, "connector_type": connector_type, "tenant_id": tenant_id, "configuration": configuration or {}})
        resp.raise_for_status()
        return resp.json()

    def list_data_sources(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"tenant_id": tenant_id} if tenant_id else {}
        resp = self.client.get("/v1/data-sources", params=params)
        resp.raise_for_status()
        return resp.json()

    def discover_schema(self, source_id: str) -> Dict[str, Any]:
        resp = self.client.post(f"/v1/data-sources/{source_id}/discover")
        resp.raise_for_status()
        return resp.json()

    def trigger_sync(self, source_id: str, strategy: str = "FULL") -> Dict[str, Any]:
        resp = self.client.post(f"/v1/data-sources/{source_id}/sync", json={"strategy": strategy})
        resp.raise_for_status()
        return resp.json()

    def list_catalog(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"tenant_id": tenant_id} if tenant_id else {}
        resp = self.client.get("/v1/data-catalog", params=params)
        resp.raise_for_status()
        return resp.json()
