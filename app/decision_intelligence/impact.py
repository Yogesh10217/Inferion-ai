"""
Multi-Dimensional Impact Assessment Subsystem.
Evaluates operational, security, financial, and compliance impact vectors for candidate decision options.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field


class MultiDimensionalImpact(BaseModel):
    impact_id: str = Field(default_factory=lambda: f"imp_{uuid.uuid4().hex[:12]}")
    decision_id: str
    tenant_id: str
    operational_impact: str = "MEDIUM"
    security_impact: str = "LOW"
    financial_impact: float = 0.0
    compliance_impact: str = "NONE"
    overall_impact_rating: str = "MEDIUM"
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ImpactAssessmentEngine:
    """Assesses multi-dimensional impacts for decision options."""

    def __init__(self) -> None:
        self._assessments: Dict[str, MultiDimensionalImpact] = {}

    def assess_impact(
        self,
        decision_id: str,
        tenant_id: str,
        operational_impact: str = "MEDIUM",
        security_impact: str = "LOW",
        financial_impact: float = 0.0,
        compliance_impact: str = "NONE",
    ) -> MultiDimensionalImpact:
        impact = MultiDimensionalImpact(
            decision_id=decision_id,
            tenant_id=tenant_id,
            operational_impact=operational_impact,
            security_impact=security_impact,
            financial_impact=financial_impact,
            compliance_impact=compliance_impact,
        )
        self._assessments[decision_id] = impact
        return impact

    def get_impact(self, decision_id: str) -> Optional[MultiDimensionalImpact]:
        return self._assessments.get(decision_id)
