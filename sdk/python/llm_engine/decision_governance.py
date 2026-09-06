"""Python SDK client for Decision Governance platform."""

from typing import Dict, Any, List, Optional


class DecisionGovernanceClient:
    """Python SDK client for managing decision governance operations."""

    def __init__(self, base_client: Any) -> None:
        self.client = base_client

    def create_decision(
        self,
        title: str,
        decision_type: str = "OPERATIONAL",
        description: str = "",
        priority: str = "MEDIUM",
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default_tenant",
    ) -> Dict[str, Any]:
        payload = {
            "title": title,
            "decision_type": decision_type,
            "description": description,
            "priority": priority,
            "metadata": metadata or {},
        }
        headers = {"x-tenant-id": tenant_id}
        return self.client.post("/v1/decisions", json=payload, headers=headers)

    def list_decisions(self, tenant_id: str = "default_tenant") -> List[Dict[str, Any]]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get("/v1/decisions", headers=headers)

    def get_decision(self, decision_id: str, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get(f"/v1/decisions/{decision_id}", headers=headers)

    def analyze_decision(self, decision_id: str, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.post(f"/v1/decisions/{decision_id}/analyze", headers=headers)

    def approve_decision(self, decision_id: str, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.post(f"/v1/decisions/{decision_id}/approve", headers=headers)

    def delegate_decision(
        self, decision_id: str, actions: List[Dict[str, Any]], tenant_id: str = "default_tenant"
    ) -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.post(f"/v1/decisions/{decision_id}/delegate", json={"actions": actions}, headers=headers)

    def verify_decision(self, decision_id: str, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.post(f"/v1/decisions/{decision_id}/verify", headers=headers)

    def explain_decision(self, decision_id: str, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get(f"/v1/decisions/{decision_id}/explain", headers=headers)

    def get_analytics_report(self, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get("/v1/decisions/analytics/reports", headers=headers)
