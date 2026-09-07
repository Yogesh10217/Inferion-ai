"""Python SDK client for Operations Assurance platform."""

from typing import Any, Dict, List, Optional


class OperationsAssuranceClient:
    """Python SDK client for managing enterprise operations intelligence, service health, and governance assurance."""

    def __init__(self, base_client: Any) -> None:
        self.client = base_client

    def register_service(
        self,
        name: str,
        service_type: str = "MICROSERVICE",
        tier: str = "TIER_1",
        criticality: str = "CRITICAL",
        tenant_id: str = "default_tenant",
    ) -> Dict[str, Any]:
        payload = {
            "name": name,
            "service_type": service_type,
            "tier": tier,
            "criticality": criticality,
        }
        headers = {"x-tenant-id": tenant_id}
        return self.client.post("/v1/operations/services", json=payload, headers=headers)

    def get_service(self, service_id: str, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get(f"/v1/operations/services/{service_id}", headers=headers)

    def get_health(self, service_id: str, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get(f"/v1/operations/services/{service_id}/health", headers=headers)

    def evaluate_assurance(self, service_id: str, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get(f"/v1/operations/services/{service_id}/assurance", headers=headers)

    def get_analytics(self, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get("/v1/operations/analytics", headers=headers)
