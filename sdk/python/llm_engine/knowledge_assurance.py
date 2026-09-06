"""Python SDK client for Knowledge Assurance platform."""

from typing import Any, Dict, List, Optional


class KnowledgeAssuranceClient:
    """Python SDK client for managing knowledge assurance, trust, context, and freshness operations."""

    def __init__(self, base_client: Any) -> None:
        self.client = base_client

    def get_status(self, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get("/v1/knowledge/status", headers=headers)

    def create_reference(
        self,
        external_key: str,
        resource_type: str = "DOCUMENT",
        classification: str = "INTERNAL",
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default_tenant",
    ) -> Dict[str, Any]:
        payload = {
            "external_key": external_key,
            "resource_type": resource_type,
            "classification": classification,
            "metadata": metadata or {},
        }
        headers = {"x-tenant-id": tenant_id}
        return self.client.post("/v1/knowledge/references", json=payload, headers=headers)

    def list_references(self, tenant_id: str = "default_tenant") -> List[Dict[str, Any]]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get("/v1/knowledge/references", headers=headers)

    def register_source(
        self,
        name: str,
        source_type: str = "DOCUMENT_REPOSITORY",
        authority: str = "AUTHORITATIVE",
        reliability_score: float = 0.95,
        tenant_id: str = "default_tenant",
    ) -> Dict[str, Any]:
        payload = {
            "name": name,
            "source_type": source_type,
            "authority": authority,
            "reliability_score": reliability_score,
        }
        headers = {"x-tenant-id": tenant_id}
        return self.client.post("/v1/knowledge/sources", json=payload, headers=headers)

    def list_sources(self, tenant_id: str = "default_tenant") -> List[Dict[str, Any]]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get("/v1/knowledge/sources", headers=headers)

    def create_context(
        self,
        title: str,
        context_type: str = "DECISION_CONTEXT",
        scope: str = "ORGANIZATION",
        priority: str = "HIGH",
        payload: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default_tenant",
    ) -> Dict[str, Any]:
        data = {
            "title": title,
            "context_type": context_type,
            "scope": scope,
            "priority": priority,
            "payload": payload or {},
        }
        headers = {"x-tenant-id": tenant_id}
        return self.client.post("/v1/knowledge/context", json=data, headers=headers)

    def assemble_context(
        self,
        target_resource_id: str,
        required_concepts: Optional[List[str]] = None,
        min_trust_score: float = 0.8,
        tenant_id: str = "default_tenant",
    ) -> Dict[str, Any]:
        data = {
            "target_resource_id": target_resource_id,
            "required_concepts": required_concepts or [],
            "min_trust_score": min_trust_score,
        }
        headers = {"x-tenant-id": tenant_id}
        return self.client.post("/v1/knowledge/context-assembly", json=data, headers=headers)

    def evaluate_trust(
        self, target_resource_id: str, tenant_id: str = "default_tenant"
    ) -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get(f"/v1/knowledge/trust/{target_resource_id}", headers=headers)

    def list_conflicts(self, tenant_id: str = "default_tenant") -> List[Dict[str, Any]]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get("/v1/knowledge/conflicts", headers=headers)

    def assess_assurance(
        self, target_resource_id: str, tenant_id: str = "default_tenant"
    ) -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get(f"/v1/knowledge/assurance/{target_resource_id}", headers=headers)

    def get_analytics_report(self, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get("/v1/knowledge/analytics/report", headers=headers)
