"""Python SDK Client for MLOps API."""

from typing import Dict, Any, List, Optional
import httpx


class MLOpsClient:
    """Python SDK client for AI Assets, Versioning, Deployments, Releases, and Drift monitoring."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=timeout)

    def create_asset(self, name: str, asset_type: str, tenant_id: str = "global", description: str = "") -> Dict[str, Any]:
        resp = self.client.post("/v1/mlops/assets", json={"name": name, "asset_type": asset_type, "tenant_id": tenant_id, "description": description})
        resp.raise_for_status()
        return resp.json()

    def list_assets(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"tenant_id": tenant_id} if tenant_id else {}
        resp = self.client.get("/v1/mlops/assets", params=params)
        resp.raise_for_status()
        return resp.json()

    def create_deployment(self, name: str, asset_id: str, version_number: str, environment: str = "DEVELOPMENT", tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.post("/v1/mlops/deployments", json={"name": name, "asset_id": asset_id, "version_number": version_number, "environment": environment, "tenant_id": tenant_id})
        resp.raise_for_status()
        return resp.json()

    def list_deployments(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"tenant_id": tenant_id} if tenant_id else {}
        resp = self.client.get("/v1/mlops/deployments", params=params)
        resp.raise_for_status()
        return resp.json()

    def rollback_deployment(self, deployment_id: str, target_version_number: str, reason: str = "") -> Dict[str, Any]:
        resp = self.client.post(f"/v1/mlops/deployments/{deployment_id}/rollback", json={"target_version_number": target_version_number, "reason": reason})
        resp.raise_for_status()
        return resp.json()
