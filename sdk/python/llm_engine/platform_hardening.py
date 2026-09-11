"""
Python SDK Client for Enterprise AI Platform Hardening & Certification.
"""

from typing import Any, Dict, Optional
import requests


class PlatformHardeningClient:
    """Python SDK client for accessing platform hardening, integration audit, and certification APIs."""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def _headers(self, tenant_id: str) -> Dict[str, str]:
        return {"X-Tenant-ID": tenant_id}

    def run_audit(self, tenant_id: str = "system", include_ast_scan: bool = True) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/platform-hardening/audit"
        payload = {"tenant_id": tenant_id, "include_ast_scan": include_ast_scan}
        resp = self.session.post(url, json=payload, headers=self._headers(tenant_id))
        resp.raise_for_status()
        return resp.json()

    def get_audit(self, audit_id: str, tenant_id: str = "system") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/platform-hardening/audit/{audit_id}"
        resp = self.session.get(url, headers=self._headers(tenant_id))
        resp.raise_for_status()
        return resp.json()

    def list_findings(self, tenant_id: str = "system") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/platform-hardening/findings"
        resp = self.session.get(url, headers=self._headers(tenant_id))
        resp.raise_for_status()
        return resp.json()

    def get_health(self, tenant_id: str = "system") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/platform-hardening/health"
        resp = self.session.get(url, headers=self._headers(tenant_id))
        resp.raise_for_status()
        return resp.json()

    def get_integration(self, tenant_id: str = "system") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/platform-hardening/integration"
        resp = self.session.get(url, headers=self._headers(tenant_id))
        resp.raise_for_status()
        return resp.json()

    def certify_platform(self, tenant_id: str = "system", force_audit: bool = False) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/platform-hardening/certify"
        payload = {"tenant_id": tenant_id, "force_audit": force_audit}
        resp = self.session.post(url, json=payload, headers=self._headers(tenant_id))
        resp.raise_for_status()
        return resp.json()

    def get_certification(self, tenant_id: str = "system") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/platform-hardening/certification"
        resp = self.session.get(url, headers=self._headers(tenant_id))
        resp.raise_for_status()
        return resp.json()

    def get_readiness(self, tenant_id: str = "system") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/platform-hardening/readiness"
        resp = self.session.get(url, headers=self._headers(tenant_id))
        resp.raise_for_status()
        return resp.json()

    def get_remediation(self, tenant_id: str = "system") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/platform-hardening/remediation"
        resp = self.session.get(url, headers=self._headers(tenant_id))
        resp.raise_for_status()
        return resp.json()

    def scan_stubs(self, tenant_id: str = "system") -> Dict[str, Any]:
        url = f"{self.base_url}/v1/platform-hardening/scan/stubs"
        resp = self.session.post(url, json={"tenant_id": tenant_id}, headers=self._headers(tenant_id))
        resp.raise_for_status()
        return resp.json()
