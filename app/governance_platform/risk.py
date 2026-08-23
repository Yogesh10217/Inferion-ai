"""Unified AI Risk Management & Deterministic Explainable Risk Scoring Engine."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RiskCategory(str, Enum):
    SECURITY = "SECURITY"
    PRIVACY = "PRIVACY"
    DATA = "DATA"
    MODEL = "MODEL"
    AGENT = "AGENT"
    AUTONOMY = "AUTONOMY"
    SAFETY = "SAFETY"
    COMPLIANCE = "COMPLIANCE"
    OPERATIONAL = "OPERATIONAL"
    FINANCIAL = "FINANCIAL"
    SUPPLY_CHAIN = "SUPPLY_CHAIN"
    THIRD_PARTY = "THIRD_PARTY"
    REPUTATIONAL = "REPUTATIONAL"


class RiskSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# Alias for backward compatibility across platform modules
RiskLevel = RiskSeverity



class RiskStatus(str, Enum):
    IDENTIFIED = "IDENTIFIED"
    ASSESSED = "ASSESSED"
    ACCEPTED = "ACCEPTED"
    MITIGATING = "MITIGATING"
    MONITORED = "MONITORED"
    ESCALATED = "ESCALATED"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class RiskFactor(BaseModel):
    name: str
    weight: float = 1.0
    impact_score: float = 10.0  # 0 to 100
    evidence_id: Optional[str] = None
    description: str = ""


class RiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"risk_{uuid.uuid4().hex[:10]}")
    target_resource_id: str
    tenant_id: str = "global"
    category: RiskCategory = RiskCategory.SECURITY

    overall_score: float = 0.0  # 0.0 to 100.0 scale
    severity: RiskSeverity = RiskSeverity.LOW
    status: RiskStatus = RiskStatus.ASSESSED

    factors: List[RiskFactor] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    calculation_version: str = "1.0.0"
    approval_request_id: Optional[str] = None
    assessed_at: datetime = Field(default_factory=_now)


class RiskManager:
    """Calculates deterministic, reproducible risk scores and manages risk acceptance approvals via ApprovalEngine."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self._assessments: Dict[str, RiskAssessment] = {}

    def calculate_risk(
        self,
        target_resource_id: str,
        factors: List[RiskFactor],
        category: RiskCategory = RiskCategory.SECURITY,
        tenant_id: str = "global",
    ) -> RiskAssessment:
        if not factors:
            total_score = 0.0
        else:
            total_weight = sum(f.weight for f in factors)
            weighted_sum = sum(f.impact_score * f.weight for f in factors)
            total_score = float(min(100.0, max(0.0, weighted_sum / total_weight if total_weight > 0 else 0.0)))

        # Determine severity threshold
        if total_score >= 85.0:
            severity = RiskSeverity.CRITICAL
        elif total_score >= 65.0:
            severity = RiskSeverity.HIGH
        elif total_score >= 35.0:
            severity = RiskSeverity.MEDIUM
        else:
            severity = RiskSeverity.LOW

        evidence = [f.evidence_id for f in factors if f.evidence_id]

        assessment = RiskAssessment(
            target_resource_id=target_resource_id,
            tenant_id=tenant_id,
            category=category,
            overall_score=total_score,
            severity=severity,
            factors=factors,
            evidence_ids=evidence,
        )
        self._assessments[assessment.assessment_id] = assessment
        logger.info(f"[RISK MANAGER] Assessed '{target_resource_id}' ({category.value}): Score = {total_score:.1f} ({severity.value})")
        return assessment

    def request_risk_acceptance(self, assessment_id: str) -> RiskAssessment:
        assessment = self.get_assessment(assessment_id)

        if assessment.severity in (RiskSeverity.HIGH, RiskSeverity.CRITICAL):
            req_id = f"risk_appr_{assessment.assessment_id[:8]}"
            assessment.approval_request_id = req_id
            assessment.status = RiskStatus.ESCALATED
            logger.warning(f"[RISK MANAGER] {assessment.severity.value} risk acceptance REQUIRES APPROVAL (Request ID: {req_id})")
        else:
            assessment.status = RiskStatus.ACCEPTED
            logger.info(f"[RISK MANAGER] {assessment.severity.value} risk accepted automatically under policy")

        return assessment

    def accept_risk(self, assessment_id: str) -> RiskAssessment:
        assessment = self.get_assessment(assessment_id)
        assessment.status = RiskStatus.ACCEPTED
        logger.info(f"[RISK MANAGER] Risk assessment '{assessment_id}' ACCEPTED by administrator.")
        return assessment

    def get_assessment(self, assessment_id: str) -> RiskAssessment:
        ass = self._assessments.get(assessment_id)
        if not ass:
            raise KeyError(f"Risk assessment '{assessment_id}' not found")
        return ass

    def list_assessments(self, tenant_id: Optional[str] = None) -> List[RiskAssessment]:
        res = list(self._assessments.values())
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        return res
