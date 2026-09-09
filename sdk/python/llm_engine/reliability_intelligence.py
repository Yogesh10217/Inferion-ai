"""Python SDK client for Reliability Intelligence (Phase 5.55)."""

from typing import Dict, Any, Optional, List
import httpx

class ReliabilityIntelligenceClient:
    """Client interface for Reliability Intelligence platform operations."""

    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def evaluate_service_health(self, tenant_id: str, service_id: str, raw_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/reliability/health"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"service_id": service_id, "metrics": raw_metrics or {}}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def evaluate_reliability(self, tenant_id: str, scope: str = "global") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/reliability/assessments"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        with httpx.Client() as client:
            res = client.post(url, json={"scope": scope}, headers=headers)
            res.raise_for_status()
            return res.json()

    def create_slo(self, tenant_id: str, service_id: str, indicator_type: str = "AVAILABILITY", target_percentage: float = 99.9) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/reliability/slo"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"service_id": service_id, "indicator_type": indicator_type, "target_percentage": target_percentage}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def predict_failure(self, tenant_id: str, service_id: str, horizon_minutes: int = 60) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/reliability/predictions"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"service_id": service_id, "horizon_minutes": horizon_minutes}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def analyze_propagation(self, tenant_id: str, origin_service: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/reliability/propagation/analyze"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        with httpx.Client() as client:
            res = client.post(url, json={"origin_service": origin_service}, headers=headers)
            res.raise_for_status()
            return res.json()

    def plan_degradation(self, tenant_id: str, service_id: str, strategy: str = "GRACEFUL") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/reliability/degradation/plan"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"service_id": service_id, "strategy": strategy}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def plan_recovery(self, tenant_id: str, service_id: str, strategy: str = "FAILOVER") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/reliability/recovery/plan"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"service_id": service_id, "strategy": strategy}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def propose_chaos_experiment(self, tenant_id: str, experiment_name: str, target_service: str, hypothesis: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/reliability/chaos/propose"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"experiment_name": experiment_name, "target_service": target_service, "hypothesis": hypothesis}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def get_analytics(self, tenant_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/reliability/analytics"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        with httpx.Client() as client:
            res = client.get(url, headers=headers)
            res.raise_for_status()
            return res.json()
