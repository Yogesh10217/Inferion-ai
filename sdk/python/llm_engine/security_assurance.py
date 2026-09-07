"""Python SDK client for Security Assurance platform."""

from typing import Any, Dict, List, Optional


class SecurityAssuranceClient:
    """Python SDK client for managing enterprise security intelligence, threat detection, and continuous security assurance."""

    def __init__(self, base_client: Any) -> None:
        self.client = base_client

    def register_asset(
        self,
        name: str,
        asset_type: str = "AI_MODEL",
        criticality: str = "MEDIUM",
        location: str = "internal",
        owner: str = "security-team",
        metadata: Optional[Dict[str, Any]] = None,
        tenant_id: str = "default_tenant",
    ) -> Dict[str, Any]:
        payload = {
            "name": name,
            "asset_type": asset_type,
            "criticality": criticality,
            "location": location,
            "owner": owner,
            "metadata": metadata or {},
        }
        headers = {"x-tenant-id": tenant_id}
        return self.client.post("/v1/security/assets", json=payload, headers=headers)

    def evaluate_posture(self, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get("/v1/security/posture", headers=headers)

    def record_threat(
        self,
        title: str,
        threat_type: str = "PROMPT_INJECTION",
        severity: str = "HIGH",
        target_asset_id: Optional[str] = None,
        description: str = "",
        indicators: Optional[List[str]] = None,
        tenant_id: str = "default_tenant",
    ) -> Dict[str, Any]:
        payload = {
            "title": title,
            "threat_type": threat_type,
            "severity": severity,
            "target_asset_id": target_asset_id,
            "description": description,
            "indicators": indicators or [],
        }
        headers = {"x-tenant-id": tenant_id}
        return self.client.post("/v1/security/threats", json=payload, headers=headers)

    def create_incident(
        self,
        title: str,
        severity: str = "HIGH",
        threat_ids: Optional[List[str]] = None,
        affected_asset_ids: Optional[List[str]] = None,
        description: str = "",
        idempotency_key: Optional[str] = None,
        tenant_id: str = "default_tenant",
    ) -> Dict[str, Any]:
        payload = {
            "title": title,
            "severity": severity,
            "threat_ids": threat_ids or [],
            "affected_asset_ids": affected_asset_ids or [],
            "description": description,
            "idempotency_key": idempotency_key,
        }
        headers = {"x-tenant-id": tenant_id}
        return self.client.post("/v1/security/incidents", json=payload, headers=headers)

    def delegate_action(
        self,
        target_system: str,
        action_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        tenant_id: str = "default_tenant",
    ) -> Dict[str, Any]:
        payload = {
            "target_system": target_system,
            "action_name": action_name,
            "parameters": parameters or {},
            "idempotency_key": idempotency_key,
        }
        headers = {"x-tenant-id": tenant_id}
        return self.client.post("/v1/security/delegation", json=payload, headers=headers)

    def evaluate_assurance(self, tenant_id: str = "default_tenant") -> Dict[str, Any]:
        headers = {"x-tenant-id": tenant_id}
        return self.client.get("/v1/security/assurance", headers=headers)
