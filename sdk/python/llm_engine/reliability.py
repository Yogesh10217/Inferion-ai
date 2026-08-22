"""Python SDK Client for Security, Governance, Jobs, and Reliability."""

from typing import Dict, Any, List, Optional
import httpx


class SecurityClient:
    """Python SDK client for API Keys & Identity."""

    def __init__(self, base_url: str = "http://localhost:8002", timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def create_api_key(self, name: str, tenant_id: str = "global", scopes: Optional[List[str]] = None) -> Dict[str, Any]:
        resp = self.client.post("/v1/security/api-keys", json={"name": name, "tenant_id": tenant_id, "scopes": scopes or ["read", "write"]})
        resp.raise_for_status()
        return resp.json()

    def list_api_keys(self, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.get("/v1/security/api-keys", params={"tenant_id": tenant_id})
        resp.raise_for_status()
        return resp.json()

    def revoke_api_key(self, key_id: str) -> Dict[str, Any]:
        resp = self.client.delete(f"/v1/security/api-keys/{key_id}")
        resp.raise_for_status()
        return resp.json()


class GovernanceClient:
    """Python SDK client for Quotas & Usage."""

    def __init__(self, base_url: str = "http://localhost:8002", timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def get_usage(self, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.get("/v1/governance/usage", params={"tenant_id": tenant_id})
        resp.raise_for_status()
        return resp.json()

    def get_quotas(self, tenant_id: str = "global") -> Dict[str, Any]:
        resp = self.client.get("/v1/governance/quotas", params={"tenant_id": tenant_id})
        resp.raise_for_status()
        return resp.json()


class JobsClient:
    """Python SDK client for Distributed Jobs."""

    def __init__(self, base_url: str = "http://localhost:8002", timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def enqueue_job(self, name: str, handler_name: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        resp = self.client.post("/v1/jobs", json={"name": name, "handler_name": handler_name, "payload": payload or {}})
        resp.raise_for_status()
        return resp.json()

    def get_job(self, job_id: str) -> Dict[str, Any]:
        resp = self.client.get(f"/v1/jobs/{job_id}")
        resp.raise_for_status()
        return resp.json()


class ReliabilityClient:
    """Python SDK client for Health & Resilience metrics."""

    def __init__(self, base_url: str = "http://localhost:8002", timeout: float = 10.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url, timeout=timeout)

    def get_health(self) -> Dict[str, Any]:
        resp = self.client.get("/v1/reliability/health")
        resp.raise_for_status()
        return resp.json()

    def get_circuit_breakers(self) -> Dict[str, Any]:
        resp = self.client.get("/v1/reliability/circuit-breakers")
        resp.raise_for_status()
        return resp.json()
