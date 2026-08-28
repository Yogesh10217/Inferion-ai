"""Python SDK Client for Enterprise AI Control Assurance (Phase 5.38)."""

from typing import Dict, Any, Optional, List
import requests


class ControlAssuranceClient:
    """Python SDK Client for Control Assurance Subsystem."""

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

    def list_controls(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        params = {}
        if category:
            params["category"] = category
        resp = requests.get(
            f"{self.base_url}/v1/control-assurance/controls",
            params=params,
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def register_control(self, code: str, name: str, description: str, category: str = "SECURITY", criticality: str = "HIGH") -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/v1/control-assurance/controls",
            params={"code": code, "name": name, "description": description, "category": category, "criticality": criticality},
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def get_control(self, control_id: str) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/v1/control-assurance/controls/{control_id}",
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def evaluate_control(self, control_id: str, scope_target_id: str = "InferenceEngine_Core") -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/v1/control-assurance/controls/{control_id}/evaluate",
            params={"scope_target_id": scope_target_id},
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def get_assurance(self, target_id: str = "InferenceEngine_Core") -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/v1/control-assurance/assurance",
            params={"target_id": target_id},
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def get_analytics(self) -> Dict[str, Any]:
        resp = requests.get(
            f"{self.base_url}/v1/control-assurance/analytics",
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def run_full_lifecycle(self) -> Dict[str, Any]:
        resp = requests.post(
            f"{self.base_url}/v1/control-assurance/lifecycle/run",
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()
