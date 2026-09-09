"""Python SDK client for Runtime Intelligence (Phase 5.54)."""

from typing import Dict, Any, Optional, List
import httpx

class RuntimeIntelligenceClient:
    """Client interface for Runtime Intelligence platform operations."""

    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def ingest_observation(self, tenant_id: str, subsystem: str, metric_name: str, value: float, dimensions: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/runtime/observations"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"subsystem": subsystem, "metric_name": metric_name, "value": value, "dimensions": dimensions or {}}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def evaluate_health(self, tenant_id: str, subsystem: str, raw_telemetry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/runtime/health"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"subsystem": subsystem, "raw_telemetry": raw_telemetry or {}}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def detect_anomalies(self, tenant_id: str, subsystem: str, time_series_data: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/runtime/anomalies"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"subsystem": subsystem, "time_series_data": time_series_data or []}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def detect_drift(self, tenant_id: str, subsystem: str, current_data: Optional[Dict[str, Any]] = None, baseline_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/runtime/drift"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"subsystem": subsystem, "current_data": current_data or {}, "baseline_data": baseline_data or {}}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def establish_baseline(self, tenant_id: str, subsystem: str, metric_name: str, sample_values: List[float]) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/runtime/baseline"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"subsystem": subsystem, "metric_name": metric_name, "sample_values": sample_values}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def analyze_causality(self, tenant_id: str, symptom_id: str, affected_subsystems: Optional[List[str]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/runtime/causal-analysis"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"symptom_id": symptom_id, "affected_subsystems": affected_subsystems or []}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def evaluate_resilience(self, tenant_id: str, subsystem: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/runtime/resilience"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"subsystem": subsystem}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def request_delegation(self, tenant_id: str, target_domain: str, action_type: str, payload: Optional[Dict[str, Any]] = None, risk_level: str = "MEDIUM") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/runtime/delegation"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"target_domain": target_domain, "action_type": action_type, "payload": payload or {}, "risk_level": risk_level}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def capture_snapshot(self, tenant_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/runtime/snapshots"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        with httpx.Client() as client:
            res = client.post(url, json={}, headers=headers)
            res.raise_for_status()
            return res.json()
