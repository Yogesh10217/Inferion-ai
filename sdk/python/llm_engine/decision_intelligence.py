"""Python SDK Client for Phase 5.52 Enterprise AI Decision Intelligence Platform."""

import requests
from typing import Dict, Any, List, Optional


class DecisionIntelligenceClient:
    """SDK client for interacting with the Decision Intelligence REST API."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, tenant_id: str = "default") -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.tenant_id = tenant_id

    def _headers(self) -> Dict[str, str]:
        headers = {"X-Tenant-ID": self.tenant_id, "Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def create_decision(
        self,
        title: str,
        description: Optional[str] = None,
        decision_type: str = "OPERATIONAL",
        scope: str = "ENTERPRISE",
        risk_level: str = "MEDIUM",
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/decisions"
        payload = {
            "title": title,
            "description": description,
            "decision_type": decision_type,
            "scope": scope,
            "risk_level": risk_level,
        }
        res = requests.post(url, json=payload, headers=self._headers())
        res.raise_for_status()
        return res.json()

    def get_decision(self, decision_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/decisions/{decision_id}"
        res = requests.get(url, headers=self._headers())
        res.raise_for_status()
        return res.json()

    def transition_state(self, decision_id: str, target_state: str, reason: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/decisions/{decision_id}/transition"
        payload = {"target_state": target_state, "reason": reason}
        res = requests.post(url, json=payload, headers=self._headers())
        res.raise_for_status()
        return res.json()

    def add_option(
        self,
        decision_id: str,
        title: str,
        action_type: str = "DELEGATE",
        target_system: str = "OPERATIONS",
        estimated_cost: float = 0.0,
        reversibility: str = "REVERSIBLE",
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/decisions/{decision_id}/options"
        payload = {
            "title": title,
            "action_type": action_type,
            "target_system": target_system,
            "estimated_cost": estimated_cost,
            "reversibility": reversibility,
        }
        res = requests.post(url, json=payload, headers=self._headers())
        res.raise_for_status()
        return res.json()

    def simulate(self, decision_id: str, scenarios: Optional[List[str]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/decisions/{decision_id}/simulate"
        payload = {"scenarios": scenarios or ["BASELINE", "HIGH_LOAD"]}
        res = requests.post(url, json=payload, headers=self._headers())
        res.raise_for_status()
        return res.json()

    def get_reproducibility(self, decision_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/decisions/{decision_id}/reproducibility"
        res = requests.get(url, headers=self._headers())
        res.raise_for_status()
        return res.json()

    def approve(self, decision_id: str, approver: str, approved: bool, comments: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/decisions/{decision_id}/approve"
        payload = {"approver": approver, "approved": approved, "comments": comments}
        res = requests.post(url, json=payload, headers=self._headers())
        res.raise_for_status()
        return res.json()

    def run_flow(self, title: str = "Enterprise AI Architecture Modernization") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/decisions/flow?title={title}"
        res = requests.post(url, headers=self._headers())
        res.raise_for_status()
        return res.json()
