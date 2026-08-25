"""Python SDK Client for Enterprise AI Reliability Platform (Phase 5.31)."""

from typing import Dict, Any, Optional, List


class SecurityClient:
    """SDK client for Security endpoints."""

    def __init__(self, client: Any = None, base_url: str = "") -> None:
        self.client = client
        self.base_url = base_url


class GovernanceClient:
    """SDK client for Governance endpoints."""

    def __init__(self, client: Any = None, base_url: str = "") -> None:
        self.client = client
        self.base_url = base_url


class JobsClient:
    """SDK client for Jobs endpoints."""

    def __init__(self, client: Any = None, base_url: str = "") -> None:
        self.client = client
        self.base_url = base_url


class ReliabilityClient:
    """SDK client for interacting with Enterprise AI Reliability Platform API."""

    def __init__(self, base_client: Any) -> None:
        self._client = base_client

    def register_service(self, tenant_id: str, name: str, tier: str = "TIER_1_HIGH") -> Dict[str, Any]:
        return self._client.post(f"/v1/reliability/services?tenant_id={tenant_id}", json={"name": name, "tier": tier})

    def create_slo(self, tenant_id: str, service_id: str, name: str, target_percentage: float = 99.9) -> Dict[str, Any]:
        return self._client.post(
            f"/v1/reliability/slos?tenant_id={tenant_id}",
            json={"service_id": service_id, "name": name, "target_percentage": target_percentage},
        )

    def create_incident(self, tenant_id: str, service_id: str, title: str, severity: str = "SEV_1_HIGH") -> Dict[str, Any]:
        return self._client.post(
            f"/v1/reliability/incidents?tenant_id={tenant_id}",
            json={"service_id": service_id, "title": title, "severity": severity},
        )

    def plan_remediation(self, tenant_id: str, incident_id: str, idempotency_key: str, action_name: str = "RESTART_POD", is_high_risk: bool = False) -> Dict[str, Any]:
        return self._client.post(
            f"/v1/reliability/remediations/plan?tenant_id={tenant_id}",
            json={"incident_id": incident_id, "idempotency_key": idempotency_key, "action_name": action_name, "is_high_risk": is_high_risk},
        )

    def create_postmortem(self, tenant_id: str, incident_id: str, summary: str, root_cause: str) -> Dict[str, Any]:
        return self._client.post(
            f"/v1/reliability/postmortems?tenant_id={tenant_id}",
            json={"incident_id": incident_id, "summary": summary, "root_cause": root_cause},
        )

    def get_analytics_report(self, tenant_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/reliability/analytics/report?tenant_id={tenant_id}")
