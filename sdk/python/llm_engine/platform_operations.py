"""Python SDK Client for Platform Operations."""

from typing import Dict, Any, List, Optional


class PlatformOperationsClient:
    """Client interface for interacting with Platform Operations REST API."""

    def __init__(self, client: Any) -> None:
        self.client = client

    def list_services(self, tenant_id: str = "global") -> List[Dict[str, Any]]:
        return self.client.get(f"/v1/platform-operations/services?tenant_id={tenant_id}")

    def create_service(self, name: str, tenant_id: str = "global", service_tier: str = "TIER_1_HIGH", description: str = "") -> Dict[str, Any]:
        payload = {"name": name, "tenant_id": tenant_id, "service_tier": service_tier, "description": description}
        return self.client.post("/v1/platform-operations/services", json=payload)

    def ingest_signal(self, source: str, signal_type: str, message: str, tenant_id: str = "global", severity: str = "INFO", service_id: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "source": source,
            "signal_type": signal_type,
            "message": message,
            "tenant_id": tenant_id,
            "severity": severity,
            "service_id": service_id,
        }
        return self.client.post("/v1/platform-operations/signals", json=payload)

    def get_incident_context(self, incident_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        return self.client.get(f"/v1/platform-operations/incidents/{incident_id}/context?tenant_id={tenant_id}")

    def get_incident_diagnosis(self, incident_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        return self.client.get(f"/v1/platform-operations/incidents/{incident_id}/diagnosis?tenant_id={tenant_id}")

    def create_remediation_plan(self, incident_id: str, service_id: str, steps: List[Dict[str, Any]], tenant_id: str = "global") -> Dict[str, Any]:
        payload = {"incident_id": incident_id, "service_id": service_id, "steps": steps, "tenant_id": tenant_id}
        return self.client.post("/v1/platform-operations/remediations", json=payload)

    def approve_remediation_plan(self, plan_id: str, approver_id: str = "admin", tenant_id: str = "global") -> Dict[str, Any]:
        return self.client.post(f"/v1/platform-operations/remediations/{plan_id}/approve?approver_id={approver_id}&tenant_id={tenant_id}")

    def execute_remediation_plan(self, plan_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        return self.client.post(f"/v1/platform-operations/remediations/{plan_id}/execute?tenant_id={tenant_id}")

    def verify_remediation_plan(self, plan_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        return self.client.get(f"/v1/platform-operations/remediations/{plan_id}/verify?tenant_id={tenant_id}")

    def list_slos(self, tenant_id: str = "global", service_id: Optional[str] = None) -> List[Dict[str, Any]]:
        url = f"/v1/platform-operations/slo?tenant_id={tenant_id}"
        if service_id:
            url += f"&service_id={service_id}"
        return self.client.get(url)

    def get_capacity(self, service_id: str, tenant_id: str = "global") -> Dict[str, Any]:
        return self.client.get(f"/v1/platform-operations/capacity?service_id={service_id}&tenant_id={tenant_id}")

    def get_analytics(self, tenant_id: str = "global") -> Dict[str, Any]:
        return self.client.get(f"/v1/platform-operations/analytics?tenant_id={tenant_id}")
