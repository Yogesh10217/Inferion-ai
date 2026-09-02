"""Python SDK Client for Enterprise AI Access Intelligence (Phase 5.39)."""

from typing import Dict, Any, Optional, List
import requests


class AccessIntelligenceClient:
    """Python SDK Client for Access Intelligence Subsystem."""

    def __init__(self, base_url: str, api_key: str, tenant_id: str = "default") -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.tenant_id = tenant_id

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "X-Tenant-ID": self.tenant_id,
            "Content-Type": "application/json",
        }

    def list_identities(self, identity_type: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {}
        if identity_type:
            params["identity_type"] = identity_type
        resp = requests.get(
            f"{self.base_url}/v1/access/identities",
            params=params,
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def register_identity(self, name: str, external_id: str, identity_type: str = "HUMAN_USER") -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/v1/access/identities",
            params={"name": name, "external_id": external_id, "identity_type": identity_type},
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def evaluate_authorization(self, subject_identity_id: str, action: str, resource_id: str, resource_type: str) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/v1/access/authorization/evaluate",
            params={
                "subject_identity_id": subject_identity_id,
                "action": action,
                "resource_id": resource_id,
                "resource_type": resource_type,
            },
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def request_privileged_access(self, requester_identity_id: str, target_role_or_entitlement: str, scope: str = "PRODUCTION", justification: str = "Admin task") -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/v1/access/privileged-access",
            params={
                "requester_identity_id": requester_identity_id,
                "target_role_or_entitlement": target_role_or_entitlement,
                "scope": scope,
                "justification": justification,
            },
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def get_analytics(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/v1/access/analytics",
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def run_full_lifecycle(self) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/v1/access/lifecycle/run",
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()
