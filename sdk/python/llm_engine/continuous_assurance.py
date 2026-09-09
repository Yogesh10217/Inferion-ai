"""Python SDK client for Continuous Assurance (Phase 5.54)."""

from typing import Dict, Any, Optional, List
import httpx

class ContinuousAssuranceClient:
    """Client interface for Continuous Assurance platform operations."""

    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def record_observation(
        self, tenant_id: str, source_domain: str, observation_type: str, payload: Dict[str, Any], severity: str = "INFO"
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/continuous-assurance/observations"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {
            "source_domain": source_domain,
            "observation_type": observation_type,
            "payload": payload,
            "severity": severity,
        }
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def evaluate_assurance(self, tenant_id: str, scope: str = "global") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/continuous-assurance/assessments"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        with httpx.Client() as client:
            res = client.post(url, json={"scope": scope}, headers=headers)
            res.raise_for_status()
            return res.json()

    def get_current_assurance(self, tenant_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/continuous-assurance/assessments/current"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        with httpx.Client() as client:
            res = client.get(url, headers=headers)
            res.raise_for_status()
            return res.json()

    def analyze_drift(self, tenant_id: str, drift_type: str, expected_state: Dict[str, Any], observed_state: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/continuous-assurance/drift/analyze"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"drift_type": drift_type, "expected_state": expected_state, "observed_state": observed_state}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def evaluate_control(self, tenant_id: str, control_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/continuous-assurance/controls/evaluate"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        with httpx.Client() as client:
            res = client.post(url, json={"control_id": control_id}, headers=headers)
            res.raise_for_status()
            return res.json()

    def verify(self, tenant_id: str, target_resource_id: str, expected_hash: str, actual_hash: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/continuous-assurance/verify"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"target_resource_id": target_resource_id, "expected_hash": expected_hash, "actual_hash": actual_hash}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def create_recommendation(self, tenant_id: str, target_control: str, action_description: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/continuous-assurance/recommendations"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"target_control": target_control, "action_description": action_description}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def evaluate_governance(self, tenant_id: str, action_type: str, risk_level: str = "MEDIUM") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/continuous-assurance/governance/evaluate"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"action_type": action_type, "risk_level": risk_level}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def create_delegation(self, tenant_id: str, action_name: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/continuous-assurance/delegations"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"action_name": action_name, "parameters": parameters or {}}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def get_analytics(self, tenant_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/continuous-assurance/analytics"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        with httpx.Client() as client:
            res = client.get(url, headers=headers)
            res.raise_for_status()
            return res.json()
