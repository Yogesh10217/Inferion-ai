"""Vulnerability Intelligence Subsystem (Phase 5.32)."""

from enum import Enum
from typing import Dict, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.security_intelligence.exceptions import VulnerabilityNotFoundException, CrossTenantSecurityAccessException
from app.platform_contracts.lifecycle import LifecycleMachine, LifecycleTransition


class VulnerabilitySeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class VulnerabilityStatus(str, Enum):
    DISCOVERED = "DISCOVERED"
    VALIDATING = "VALIDATING"
    CONFIRMED = "CONFIRMED"
    RISK_ASSESSED = "RISK_ASSESSED"
    REMEDIATION_PLANNED = "REMEDIATION_PLANNED"
    REMEDIATION_IN_PROGRESS = "REMEDIATION_IN_PROGRESS"
    VERIFIED = "VERIFIED"
    CLOSED = "CLOSED"


class VulnerabilityEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: f"vev_{uuid.uuid4().hex[:12]}")
    cve_id: Optional[str] = None
    description: str


class SecurityVulnerability(BaseModel):
    vulnerability_id: str = Field(default_factory=lambda: f"vuln_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    title: str
    severity: VulnerabilitySeverity = VulnerabilitySeverity.HIGH
    status: VulnerabilityStatus = VulnerabilityStatus.DISCOVERED
    evidence: Optional[VulnerabilityEvidence] = None
    discovered_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VulnerabilityManager:
    """Manages vulnerabilities across code, packages, models, agents, and infrastructure."""

    def __init__(self) -> None:
        self._vulns: Dict[str, SecurityVulnerability] = {}
        self.lifecycle_machine = LifecycleMachine(
            name="VulnerabilityLifecycle",
            initial_state=VulnerabilityStatus.DISCOVERED.value,
            valid_transitions=[
                LifecycleTransition(from_state="DISCOVERED", to_state="VALIDATING"),
                LifecycleTransition(from_state="VALIDATING", to_state="CONFIRMED"),
                LifecycleTransition(from_state="CONFIRMED", to_state="RISK_ASSESSED"),
                LifecycleTransition(from_state="RISK_ASSESSED", to_state="REMEDIATION_PLANNED"),
                LifecycleTransition(from_state="REMEDIATION_PLANNED", to_state="REMEDIATION_IN_PROGRESS"),
                LifecycleTransition(from_state="REMEDIATION_IN_PROGRESS", to_state="VERIFIED"),
                LifecycleTransition(from_state="VERIFIED", to_state="CLOSED"),
            ],
            terminal_states={"CLOSED"},
        )

    def create_vulnerability(
        self,
        tenant_id: str,
        asset_id: str,
        title: str,
        severity: VulnerabilitySeverity = VulnerabilitySeverity.HIGH,
        cve_id: Optional[str] = None,
    ) -> SecurityVulnerability:
        ev = VulnerabilityEvidence(cve_id=cve_id, description=f"Evidence for {title}")
        vuln = SecurityVulnerability(
            tenant_id=tenant_id,
            asset_id=asset_id,
            title=title,
            severity=severity,
            evidence=ev,
        )
        self._vulns[vuln.vulnerability_id] = vuln
        return vuln

    def transition_vulnerability(
        self,
        vulnerability_id: str,
        tenant_id: str,
        target_status: VulnerabilityStatus,
    ) -> SecurityVulnerability:
        vuln = self.get_vulnerability(vulnerability_id, tenant_id)
        self.lifecycle_machine.validate_transition(vuln.status.value, target_status.value)
        vuln.status = target_status
        return vuln

    def get_vulnerability(self, vulnerability_id: str, tenant_id: str) -> SecurityVulnerability:
        vuln = self._vulns.get(vulnerability_id)
        if not vuln:
            raise VulnerabilityNotFoundException(vulnerability_id)
        if tenant_id != "global" and vuln.tenant_id != "global" and tenant_id != vuln.tenant_id:
            raise CrossTenantSecurityAccessException(tenant_id, vuln.tenant_id)
        return vuln
