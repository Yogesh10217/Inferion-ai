"""Python SDK client for Identity Assurance platform."""

from typing import Any, Dict, List, Optional


class IdentityAssuranceClient:
    """Python SDK client for managing identity assurance, trust, privileges, access reviews, and governance."""

    def __init__(self, base_client: Any) -> None:
        self.client = base_client

    def register_identity(
        self,
        name: str,
        identity_type: str = "HUMAN",
        category: str = "EMPLOYEE",
        external_id: Optional[str] = None,
        tenant_id: str = "default_tenant",
    ) -> Dict[str, Any]:
        payload = {
            "name": name,
            "identity_type": identity_type,
            "category": category,
            "external_id": external_id,
        }
        headers = {"x-tenant-id": tenant_id}
        return self.client.post("/v1/identities", json=payload, headers=headers)

    def get_identity(self, identity_id: str, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get(f"/v1/identities/{identity_id}", headers=headers)

    def assess_trust(self, identity_id: str, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.post(f"/v1/identities/{identity_id}/trust", headers=headers)

    def assess_privileges(self, identity_id: str, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.post(f"/v1/identities/{identity_id}/privileges", headers=headers)

    def evaluate_assurance(self, identity_id: str, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get(f"/v1/identities/{identity_id}/assurance", headers=headers)

    def get_analytics(self, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get("/v1/identities/analytics", headers=headers)
