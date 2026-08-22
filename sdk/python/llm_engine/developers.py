"""Python SDK Client for Developers & Events API."""

from typing import Dict, Any, List, Optional
import httpx


class DevelopersClient:
    """Python SDK client for developer accounts, projects, and webhook subscriptions."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=timeout)

    def register_developer(self, user_id: str, full_name: str, email: str, tenant_id: str = "global", company: Optional[str] = None) -> Dict[str, Any]:
        resp = self.client.post("/v1/developers", json={"user_id": user_id, "full_name": full_name, "email": email, "tenant_id": tenant_id, "company": company})
        resp.raise_for_status()
        return resp.json()

    def create_project(self, name: str, organization_id: str, workspace_id: str, developer_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.post("/v1/developers/projects", json={"name": name, "organization_id": organization_id, "workspace_id": workspace_id, "developer_id": developer_id, "tenant_id": tenant_id})
        resp.raise_for_status()
        return resp.json()

    def list_projects(self, tenant_id: Optional[str] = None, developer_id: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if tenant_id: params["tenant_id"] = tenant_id
        if developer_id: params["developer_id"] = developer_id
        resp = self.client.get("/v1/developers/projects", params=params)
        resp.raise_for_status()
        return resp.json()

    def create_webhook_subscription(self, developer_id: str, target_url: str, event_types: List[str], tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.post("/v1/events/subscriptions", json={"developer_id": developer_id, "target_url": target_url, "event_types": event_types, "tenant_id": tenant_id})
        resp.raise_for_status()
        return resp.json()
