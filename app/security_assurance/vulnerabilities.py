"""Vulnerability Management Data Models & Store."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.security_assurance.exceptions import (
    CrossTenantSecurityAssuranceException,
    SecurityVulnerabilityNotFoundException,
)


class VulnerabilitySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SecurityVulnerability(BaseModel):
    vulnerability_id: str = Field(default_factory=lambda: f"vuln-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    title: str
    severity: VulnerabilitySeverity
    asset_id: str
    cve_id: Optional[str] = None
    cvss_score: float = 0.0
    description: str = ""
    status: str = "OPEN"  # OPEN, MITIGATED, RESOLVED
    remediation_guidance: str = ""
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityVulnerabilityStore:
    """In-memory store for asset vulnerabilities."""

    def __init__(self) -> None:
        self._vulns: Dict[str, SecurityVulnerability] = {}

    def record_vulnerability(
        self,
        tenant_id: str,
        title: str,
        severity: VulnerabilitySeverity,
        asset_id: str,
        cve_id: Optional[str] = None,
        cvss_score: float = 0.0,
        description: str = "",
        remediation_guidance: str = "",
    ) -> SecurityVulnerability:
        vuln = SecurityVulnerability(
            tenant_id=tenant_id,
            title=title,
            severity=severity,
            asset_id=asset_id,
            cve_id=cve_id,
            cvss_score=cvss_score,
            description=description,
            remediation_guidance=remediation_guidance,
        )
        self._vulns[vuln.vulnerability_id] = vuln
        return vuln

    def get_vulnerability(self, tenant_id: str, vulnerability_id: str) -> SecurityVulnerability:
        vuln = self._vulns.get(vulnerability_id)
        if not vuln:
            raise SecurityVulnerabilityNotFoundException(f"Vulnerability '{vulnerability_id}' not found.")
        if vuln.tenant_id != tenant_id:
            raise CrossTenantSecurityAssuranceException(f"Tenant '{tenant_id}' cannot access vulnerability for tenant '{vuln.tenant_id}'.")
        return vuln

    def list_vulnerabilities(self, tenant_id: str, asset_id: Optional[str] = None, status: Optional[str] = None) -> List[SecurityVulnerability]:
        results = [v for v in self._vulns.values() if v.tenant_id == tenant_id]
        if asset_id:
            results = [v for v in results if v.asset_id == asset_id]
        if status:
            results = [v for v in results if v.status == status]
        return results
