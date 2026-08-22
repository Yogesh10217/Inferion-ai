"""Python SDK Client for Operations API."""

from typing import Dict, Any, List, Optional
import httpx


class OperationsClient:
    """Python SDK client for Operations, SRE, Incident Management, SLOs, Runbooks, and Autonomous Remediation."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        headers = {"Content-Type": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self.client = httpx.Client(base_url=self.base_url, headers=headers, timeout=timeout)

    def get_health(self) -> Dict[str, Any]:

        resp = self.client.get("/v1/operations/health")
        resp.raise_for_status()
        return resp.json()

    def get_topology(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"tenant_id": tenant_id} if tenant_id else {}
        resp = self.client.get("/v1/operations/topology", params=params)
        resp.raise_for_status()
        return resp.json()

    def list_slos(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"tenant_id": tenant_id} if tenant_id else {}
        resp = self.client.get("/v1/operations/slos", params=params)
        resp.raise_for_status()
        return resp.json()

    def list_alerts(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"tenant_id": tenant_id} if tenant_id else {}
        resp = self.client.get("/v1/operations/alerts", params=params)
        resp.raise_for_status()
        return resp.json()

    def list_incidents(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        params = {"tenant_id": tenant_id} if tenant_id else {}
        resp = self.client.get("/v1/operations/incidents", params=params)
        resp.raise_for_status()
        return resp.json()

    def get_incident(self, incident_id: str) -> Dict[str, Any]:
        resp = self.client.get(f"/v1/operations/incidents/{incident_id}")
        resp.raise_for_status()
        return resp.json()

    def get_root_cause(self, incident_id: str) -> Dict[str, Any]:
        resp = self.client.get(f"/v1/operations/incidents/{incident_id}/root-cause")
        resp.raise_for_status()
        return resp.json()

    def execute_runbook(self, runbook_id: str, dry_run: bool = False) -> Dict[str, Any]:
        endpoint = f"/v1/operations/runbooks/{runbook_id}/dry-run" if dry_run else f"/v1/operations/runbooks/{runbook_id}/execute"
        resp = self.client.post(endpoint)
        resp.raise_for_status()
        return resp.json()
