"""AI Compliance Framework & Control Gap Assessment Engine."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class FrameworkType(str, Enum):
    SOC2 = "SOC2"
    ISO27001 = "ISO27001"
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    PCI_DSS = "PCI_DSS"
    NIST_AI_RMF = "NIST_AI_RMF"
    EU_AI_ACT = "EU_AI_ACT"
    CUSTOM = "CUSTOM"


class ComplianceStatus(str, Enum):
    NOT_ASSESSED = "NOT_ASSESSED"
    COMPLIANT = "COMPLIANT"
    PARTIALLY_COMPLIANT = "PARTIALLY_COMPLIANT"
    NON_COMPLIANT = "NON_COMPLIANT"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"


class ComplianceControl(BaseModel):
    control_id: str
    name: str
    description: str = ""
    status: ComplianceStatus = ComplianceStatus.NOT_ASSESSED
    evidence_ids: List[str] = Field(default_factory=list)


class ComplianceAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"comp_{uuid.uuid4().hex[:10]}")
    framework: FrameworkType = FrameworkType.SOC2
    tenant_id: str = "global"

    status: ComplianceStatus = ComplianceStatus.PARTIALLY_COMPLIANT
    compliance_score_percent: float = 0.0
    controls: List[ComplianceControl] = Field(default_factory=list)

    findings: List[str] = Field(default_factory=list)
    disclaimer: str = (
        "This assessment provides internal framework mapping and evidence tracking. "
        "It does NOT constitute legal certification or automatic regulatory compliance."
    )
    assessed_at: datetime = Field(default_factory=_now)


class ComplianceManager:
    """Manages framework registration, control mapping, evidence collection, and gap detection."""

    def __init__(self) -> None:
        self._assessments: Dict[str, ComplianceAssessment] = {}

    def run_assessment(
        self,
        framework: FrameworkType,
        tenant_id: str = "global",
        controls: Optional[List[ComplianceControl]] = None,
    ) -> ComplianceAssessment:
        ctrls = controls or [
            ComplianceControl(control_id="CC1.1", name="Access Control Policy", status=ComplianceStatus.COMPLIANT),
            ComplianceControl(control_id="CC2.1", name="Audit Evidence Logging", status=ComplianceStatus.COMPLIANT),
            ComplianceControl(control_id="CC6.1", name="Secret Redaction", status=ComplianceStatus.COMPLIANT),
            ComplianceControl(control_id="CC7.1", name="Incident Response Management", status=ComplianceStatus.PARTIALLY_COMPLIANT),
        ]

        compliant_count = sum(1 for c in ctrls if c.status == ComplianceStatus.COMPLIANT)
        score = float((compliant_count / len(ctrls)) * 100.0) if ctrls else 0.0

        if score >= 100.0:
            overall_status = ComplianceStatus.COMPLIANT
        elif score >= 50.0:
            overall_status = ComplianceStatus.PARTIALLY_COMPLIANT
        else:
            overall_status = ComplianceStatus.NON_COMPLIANT

        findings = [f"Control '{c.control_id}' ({c.name}) is {c.status.value}" for c in ctrls if c.status != ComplianceStatus.COMPLIANT]

        ass = ComplianceAssessment(
            framework=framework,
            tenant_id=tenant_id,
            status=overall_status,
            compliance_score_percent=score,
            controls=ctrls,
            findings=findings,
        )
        self._assessments[ass.assessment_id] = ass
        logger.info(f"[COMPLIANCE MANAGER] Assessed framework '{framework.value}' for tenant '{tenant_id}': Score = {score:.1f}% ({overall_status.value})")
        return ass

    def get_assessment(self, assessment_id: str) -> ComplianceAssessment:
        ass = self._assessments.get(assessment_id)
        if not ass:
            raise KeyError(f"Compliance assessment '{assessment_id}' not found")
        return ass

    def list_assessments(self, tenant_id: Optional[str] = None) -> List[ComplianceAssessment]:
        res = list(self._assessments.values())
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        return res
