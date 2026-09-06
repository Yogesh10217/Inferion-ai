"""Decision impact analysis across 7 organizational dimensions."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.decision_governance.exceptions import CrossTenantDecisionGovernanceException


class ImpactDimension(str, Enum):
    BUSINESS = "BUSINESS"
    FINANCIAL = "FINANCIAL"
    OPERATIONAL = "OPERATIONAL"
    SECURITY = "SECURITY"
    COMPLIANCE = "COMPLIANCE"
    CUSTOMER = "CUSTOMER"
    RELIABILITY = "RELIABILITY"


class ImpactSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    SEVERE = "SEVERE"


class ImpactEvidence(BaseModel):
    metric_name: str
    baseline_value: float
    projected_value: float
    confidence: float = 0.9


class DecisionImpact(BaseModel):
    dimension: ImpactDimension
    severity: ImpactSeverity = ImpactSeverity.MEDIUM
    impact_score: float = 0.5
    summary: str
    evidence: List[ImpactEvidence] = Field(default_factory=list)


class ImpactAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    tenant_id: str
    impacts: List[DecisionImpact] = Field(default_factory=list)
    overall_impact_score: float = 0.5
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionImpactManager:
    """Manages decision impact evaluation across business and technical dimensions."""

    def __init__(self) -> None:
        self._assessments: Dict[str, ImpactAssessment] = {}

    def assess_impact(
        self,
        tenant_id: str,
        decision_id: str,
        custom_impacts: Optional[List[DecisionImpact]] = None,
    ) -> ImpactAssessment:
        if not custom_impacts:
            custom_impacts = [
                DecisionImpact(
                    dimension=ImpactDimension.FINANCIAL,
                    severity=ImpactSeverity.LOW,
                    impact_score=0.2,
                    summary="Estimated spend reduction of $250/mo",
                    evidence=[ImpactEvidence(metric_name="monthly_cost_usd", baseline_value=1200.0, projected_value=950.0)],
                ),
                DecisionImpact(
                    dimension=ImpactDimension.RELIABILITY,
                    severity=ImpactSeverity.LOW,
                    impact_score=0.1,
                    summary="Availability SLA maintained at 99.99%",
                    evidence=[ImpactEvidence(metric_name="uptime_pct", baseline_value=99.99, projected_value=99.99)],
                ),
            ]

        avg_score = sum(i.impact_score for i in custom_impacts) / len(custom_impacts) if custom_impacts else 0.5

        assessment = ImpactAssessment(
            tenant_id=tenant_id,
            decision_id=decision_id,
            impacts=custom_impacts,
            overall_impact_score=avg_score,
        )
        self._assessments[assessment.assessment_id] = assessment
        return assessment
