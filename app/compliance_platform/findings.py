"""Compliance Finding Management Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.compliance_platform.exceptions import ComplianceFindingException


class FindingSeverity(str, Enum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class FindingStatus(str, Enum):
    OPEN = "OPEN"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    IN_PROGRESS = "IN_PROGRESS"
    MITIGATED = "MITIGATED"
    RESOLVED = "RESOLVED"
    ACCEPTED_RISK = "ACCEPTED_RISK"
    FALSE_POSITIVE = "FALSE_POSITIVE"


class FindingCategory(str, Enum):
    CONTROL_FAILURE = "CONTROL_FAILURE"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    UNAUTHORIZED_CHANGE = "UNAUTHORIZED_CHANGE"
    GOVERNANCE_VIOLATION = "GOVERNANCE_VIOLATION"
    SECURITY_RISK = "SECURITY_RISK"


class ComplianceFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: f"find_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    control_id: Optional[str] = None
    requirement_id: Optional[str] = None
    title: str
    description: str
    severity: FindingSeverity = FindingSeverity.MEDIUM
    status: FindingStatus = FindingStatus.OPEN
    category: FindingCategory = FindingCategory.CONTROL_FAILURE
    evidence_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FindingManager:
    """Manages compliance findings and lifecycle state transitions."""

    def __init__(self) -> None:
        self._findings: Dict[str, ComplianceFinding] = {}

    def create_finding(
        self,
        tenant_id: str,
        title: str,
        description: str,
        severity: FindingSeverity = FindingSeverity.MEDIUM,
        category: FindingCategory = FindingCategory.CONTROL_FAILURE,
        control_id: Optional[str] = None,
        requirement_id: Optional[str] = None,
        evidence_ids: Optional[List[str]] = None,
    ) -> ComplianceFinding:
        finding = ComplianceFinding(
            tenant_id=tenant_id,
            title=title,
            description=description,
            severity=severity,
            category=category,
            control_id=control_id,
            requirement_id=requirement_id,
            evidence_ids=evidence_ids or [],
        )
        self._findings[finding.finding_id] = finding
        return finding

    def get_finding(self, finding_id: str, tenant_id: str) -> ComplianceFinding:
        f = self._findings.get(finding_id)
        if not f or f.tenant_id != tenant_id:
            raise ComplianceFindingException(f"Finding '{finding_id}' not found for tenant '{tenant_id}'.")
        return f

    def update_status(self, finding_id: str, tenant_id: str, status: FindingStatus) -> ComplianceFinding:
        f = self.get_finding(finding_id, tenant_id)
        f.status = status
        f.updated_at = datetime.now(timezone.utc)
        return f

    def list_findings(self, tenant_id: str, status: Optional[FindingStatus] = None) -> List[ComplianceFinding]:
        findings = [f for f in self._findings.values() if f.tenant_id == tenant_id]
        if status:
            findings = [f for f in findings if f.status == status]
        return findings
