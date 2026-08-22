"""Python SDK Client for Enterprise Control Plane & Platform Management."""

from typing import Dict, Any, List, Optional
import httpx


class ControlPlaneClient:
    """Python SDK client for Tenants, Organizations, Workspaces, Resources, Config, Policies, and Features."""

    def __init__(self, base_url: str = "http://localhost:8002", api_key: Optional[str] = None, timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=timeout)


    def get_summary(self) -> Dict[str, Any]:
        resp = self.client.get("/v1/control-plane/summary")
        resp.raise_for_status()
        return resp.json()

    def create_tenant(self, name: str, slug: Optional[str] = None) -> Dict[str, Any]:
        resp = self.client.post("/v1/control-plane/tenants", json={"name": name, "slug": slug})
        resp.raise_for_status()
        return resp.json()

    def list_tenants(self) -> Dict[str, Any]:
        resp = self.client.get("/v1/control-plane/tenants")
        resp.raise_for_status()
        return resp.json()

    def get_tenant(self, tenant_id: str) -> Dict[str, Any]:
        resp = self.client.get(f"/v1/control-plane/tenants/{tenant_id}")
        resp.raise_for_status()
        return resp.json()

    def suspend_tenant(self, tenant_id: str) -> Dict[str, Any]:
        resp = self.client.post(f"/v1/control-plane/tenants/{tenant_id}/suspend")
        resp.raise_for_status()
        return resp.json()

    def activate_tenant(self, tenant_id: str) -> Dict[str, Any]:
        resp = self.client.post(f"/v1/control-plane/tenants/{tenant_id}/activate")
        resp.raise_for_status()
        return resp.json()

    def create_organization(self, name: str, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.post("/v1/control-plane/organizations", json={"name": name, "tenant_id": tenant_id})
        resp.raise_for_status()
        return resp.json()

    def list_organizations(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"tenant_id": tenant_id} if tenant_id else {}
        resp = self.client.get("/v1/control-plane/organizations", params=params)
        resp.raise_for_status()
        return resp.json()

    def create_workspace(self, name: str, organization_id: str, tenant_id: str = "global", environment: str = "DEVELOPMENT") -> Dict[str, Any]:
        resp = self.client.post("/v1/control-plane/workspaces", json={"name": name, "organization_id": organization_id, "tenant_id": tenant_id, "environment": environment})
        resp.raise_for_status()
        return resp.json()

    def list_workspaces(self, tenant_id: Optional[str] = None, organization_id: Optional[str] = None) -> Dict[str, Any]:
        params = {}
        if tenant_id: params["tenant_id"] = tenant_id
        if organization_id: params["organization_id"] = organization_id
        resp = self.client.get("/v1/control-plane/workspaces", params=params)
        resp.raise_for_status()
        return resp.json()

    def list_resources(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"tenant_id": tenant_id} if tenant_id else {}
        resp = self.client.get("/v1/control-plane/resources", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_configuration(self, scope: str, target_id: str) -> Dict[str, Any]:
        resp = self.client.get("/v1/control-plane/configuration", params={"scope": scope, "target_id": target_id})
        resp.raise_for_status()
        return resp.json()

    def update_configuration(self, scope: str, target_id: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        resp = self.client.post("/v1/control-plane/configuration", json={"scope": scope, "target_id": target_id, "settings": settings})
        resp.raise_for_status()
        return resp.json()

    def rollback_configuration(self, scope: str, target_id: str, version: int) -> Dict[str, Any]:
        resp = self.client.post(f"/v1/control-plane/configuration/{version}/rollback", params={"scope": scope, "target_id": target_id})
        resp.raise_for_status()
        return resp.json()

    def create_policy(self, name: str, target_type: str, rules: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        resp = self.client.post("/v1/control-plane/policies", json={"name": name, "target_type": target_type, "rules": rules or {}})
        resp.raise_for_status()
        return resp.json()

    def list_policies(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"tenant_id": tenant_id} if tenant_id else {}
        resp = self.client.get("/v1/control-plane/policies", params=params)
        resp.raise_for_status()
        return resp.json()

    def simulate_policy(self, policy_id: str) -> Dict[str, Any]:
        resp = self.client.post(f"/v1/control-plane/policies/{policy_id}/simulate")
        resp.raise_for_status()
        return resp.json()

    def list_features(self) -> Dict[str, Any]:
        resp = self.client.get("/v1/control-plane/features")
        resp.raise_for_status()
        return resp.json()

    def execute_admin_operation(self, action: str, target_id: str, approved: bool = False) -> Dict[str, Any]:
        resp = self.client.post("/v1/control-plane/operations", json={"action": action, "target_id": target_id, "approved": approved})
        resp.raise_for_status()
        return resp.json()

    def get_usage_report(self, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.get("/v1/control-plane/usage", params={"tenant_id": tenant_id})
        resp.raise_for_status()
        return resp.json()
