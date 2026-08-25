"""Python SDK Client for Enterprise AI Security Intelligence Platform (Phase 5.32)."""

from typing import Dict, Any, Optional, List


class SecurityClient:
    """SDK client for interacting with Enterprise AI Security Intelligence Platform API."""

    def __init__(self, base_client: Any = None, base_url: str = "") -> None:
        self._client = base_client
        self.base_url = base_url

    def register_asset(self, tenant_id: str, name: str, asset_type: str = "MODEL_GATEWAY", criticality: str = "HIGH") -> Dict[str, Any]:
        return self._client.post(f"/v1/security/assets?tenant_id={tenant_id}", json={"name": name, "asset_type": asset_type, "criticality": criticality})

    def ingest_signal(self, tenant_id: str, asset_id: str, signal_type: str, severity: str = "HIGH", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return self._client.post(f"/v1/security/signals?tenant_id={tenant_id}", json={"asset_id": asset_id, "signal_type": signal_type, "severity": severity, "payload": payload or {}})

    def create_threat(self, tenant_id: str, asset_id: str, threat_type: str, severity: str = "HIGH") -> Dict[str, Any]:
        return self._client.post(f"/v1/security/threats?tenant_id={tenant_id}", json={"asset_id": asset_id, "threat_type": threat_type, "severity": severity})

    def analyze_ai_threat(self, tenant_id: str, model_or_agent_id: str, threat_type: str = "PROMPT_INJECTION", severity: str = "HIGH") -> Dict[str, Any]:
        return self._client.post(f"/v1/security/ai-threats?tenant_id={tenant_id}", json={"model_or_agent_id": model_or_agent_id, "threat_type": threat_type, "severity": severity})

    def create_vulnerability(self, tenant_id: str, asset_id: str, title: str, severity: str = "HIGH", cve_id: Optional[str] = None) -> Dict[str, Any]:
        return self._client.post(f"/v1/security/vulnerabilities?tenant_id={tenant_id}", json={"asset_id": asset_id, "title": title, "severity": severity, "cve_id": cve_id})

    def create_incident(self, tenant_id: str, asset_id: str, title: str, severity: str = "SEV_1_HIGH") -> Dict[str, Any]:
        return self._client.post(f"/v1/security/incidents?tenant_id={tenant_id}", json={"asset_id": asset_id, "title": title, "severity": severity})

    def plan_remediation(self, tenant_id: str, incident_id: str, idempotency_key: str, action_name: str = "REVOKE_KEY", priority: str = "HIGH") -> Dict[str, Any]:
        return self._client.post(f"/v1/security/remediation/plan?tenant_id={tenant_id}", json={"incident_id": incident_id, "idempotency_key": idempotency_key, "action_name": action_name, "priority": priority})

    def get_posture(self, tenant_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/security/posture?tenant_id={tenant_id}")

    def get_analytics_report(self, tenant_id: str) -> Dict[str, Any]:
        return self._client.get(f"/v1/security/analytics/report?tenant_id={tenant_id}")


class SecurityIntelligenceClient(SecurityClient):
    pass
