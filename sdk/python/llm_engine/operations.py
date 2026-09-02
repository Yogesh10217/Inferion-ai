"""Python SDK Client for Operations Intelligence Platform (Phase 5.41)."""

from typing import Dict, Any, List, Optional
import httpx


class OperationsClient:
    """Python SDK client for Operations, Service Management, Incidents, Major Incidents, Alerts, and RCA."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=timeout)

    def register_service(self, tenant_id: str, name: str, owner_team: str, criticality: str = "BUSINESS_CRITICAL", tier: str = "TIER_1") -> Dict[str, Any]:
        resp = self.client.post("/v1/operations/services", json={
            "tenant_id": tenant_id,
            "name": name,
            "owner_team": owner_team,
            "criticality": criticality,
            "tier": tier,
        })
        resp.raise_for_status()
        return resp.json()

    def list_services(self, tenant_id: str = "global") -> List[Dict[str, Any]]:
        resp = self.client.get(f"/v1/operations/services?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()

    def ingest_alert(self, tenant_id: str, source_system: str, service_id: str, alert_name: str, fingerprint: str, severity: str = "HIGH") -> Dict[str, Any]:
        resp = self.client.post("/v1/operations/alerts/ingest", json={
            "tenant_id": tenant_id,
            "source_system": source_system,
            "service_id": service_id,
            "alert_name": alert_name,
            "fingerprint": fingerprint,
            "severity": severity,
        })
        resp.raise_for_status()
        return resp.json()

    def list_alerts(self, tenant_id: str = "global") -> List[Dict[str, Any]]:
        resp = self.client.get(f"/v1/operations/alerts?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()

    def create_incident(self, tenant_id: str, title: str, affected_service_id: str, severity: str = "P2_HIGH", priority: str = "P2") -> Dict[str, Any]:
        resp = self.client.post("/v1/operations/incidents", json={
            "tenant_id": tenant_id,
            "title": title,
            "affected_service_id": affected_service_id,
            "severity": severity,
            "priority": priority,
        })
        resp.raise_for_status()
        return resp.json()

    def list_incidents(self, tenant_id: str = "global") -> List[Dict[str, Any]]:
        resp = self.client.get(f"/v1/operations/incidents?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()

    def declare_major_incident(self, tenant_id: str, incident_id: str, title: str, impact: str = "CRITICAL_BUSINESS_HALT") -> Dict[str, Any]:
        resp = self.client.post("/v1/operations/major-incidents/declare", json={
            "tenant_id": tenant_id,
            "incident_id": incident_id,
            "title": title,
            "impact": impact,
        })
        resp.raise_for_status()
        return resp.json()

    def get_analytics(self, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.get(f"/v1/operations/analytics?tenant_id={tenant_id}")
        resp.raise_for_status()
        return resp.json()


OperationsIntelligenceClient = OperationsClient
