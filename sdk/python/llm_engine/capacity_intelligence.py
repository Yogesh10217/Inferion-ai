"""Python SDK client for Capacity Intelligence (Phase 5.56)."""

from typing import Dict, Any, Optional, List
import httpx

class CapacityIntelligenceClient:
    """Client interface for Capacity Intelligence platform operations."""

    def __init__(self, base_url: str, api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

    def register_resource(self, tenant_id: str, resource_id: str, name: str, resource_type: str, total_capacity: float, capacity_unit: str = "units") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/capacity/resources"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"resource_id": resource_id, "name": name, "resource_type": resource_type, "total_capacity": total_capacity, "capacity_unit": capacity_unit}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def ingest_telemetry(self, tenant_id: str, resource_id: str, metric_name: str, value: float, timestamp: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/capacity/telemetry"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"resource_id": resource_id, "metric_name": metric_name, "value": value}
        if timestamp:
            body["timestamp"] = timestamp
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def assess_capacity(self, tenant_id: str, resource_id: str, scope: str = "RESOURCE") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/capacity/assessments"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"resource_id": resource_id, "scope": scope}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def forecast_capacity(self, tenant_id: str, resource_id: str, horizon_days: int = 30) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/capacity/forecasts"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"resource_id": resource_id, "horizon_days": horizon_days}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def predict_demand(self, tenant_id: str, workload_type: str, time_horizon_hours: int = 24) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/capacity/demand"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"workload_type": workload_type, "time_horizon_hours": time_horizon_hours}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def analyze_saturation(self, tenant_id: str, resource_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/capacity/saturation"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"resource_id": resource_id}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def detect_bottlenecks(self, tenant_id: str, system_scope: str = "GLOBAL") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/capacity/bottlenecks"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"system_scope": system_scope}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def optimize_capacity(self, tenant_id: str, resource_id: str, objective: str = "COST_PERFORMANCE") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/capacity/optimizations"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"resource_id": resource_id, "objective": objective}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def request_delegation(self, tenant_id: str, target_domain: str, action_type: str, payload: Optional[Dict[str, Any]] = None, risk_level: str = "MEDIUM") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/capacity/delegation"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        body = {"target_domain": target_domain, "action_type": action_type, "payload": payload or {}, "risk_level": risk_level}
        with httpx.Client() as client:
            res = client.post(url, json=body, headers=headers)
            res.raise_for_status()
            return res.json()

    def capture_snapshot(self, tenant_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/capacity/snapshots"
        headers = {**self.headers, "X-Tenant-ID": tenant_id}
        with httpx.Client() as client:
            res = client.post(url, json={}, headers=headers)
            res.raise_for_status()
            return res.json()
