"""Identity Impact Intelligence."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class IdentityImpactDimension(str, Enum):
    APPLICATIONS = "APPLICATIONS"
    DATA = "DATA"
    MODELS = "MODELS"
    AGENTS = "AGENTS"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    WORKFLOWS = "WORKFLOWS"
    BUSINESS_UNITS = "BUSINESS_UNITS"


class IdentityImpactAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    impacted_dimensions: List[IdentityImpactDimension] = Field(default_factory=list)
    impact_score: float = 0.2  # 0.0 to 1.0
    impacted_entities_count: int = 5
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityImpactManager:
    """Analyzes potential impact of identity actions across enterprise assets."""

    def __init__(self) -> None:
        self._assessments: Dict[str, IdentityImpactAssessment] = {}

    def assess_impact(
        self,
        tenant_id: str,
        identity_id: str,
        dimensions: Optional[List[IdentityImpactDimension]] = None,
    ) -> IdentityImpactAssessment:
        dim_list = dimensions or [
            IdentityImpactDimension.APPLICATIONS,
            IdentityImpactDimension.DATA,
            IdentityImpactDimension.AGENTS,
        ]
        impact_score = min(1.0, len(dim_list) * 0.15)

        assessment = IdentityImpactAssessment(
            identity_id=identity_id,
            tenant_id=tenant_id,
            impacted_dimensions=dim_list,
            impact_score=round(impact_score, 4),
            impacted_entities_count=len(dim_list) * 3,
        )
        self._assessments[identity_id] = assessment
        return assessment

    def get_assessment(self, tenant_id: str, identity_id: str) -> IdentityImpactAssessment:
        assessment = self._assessments.get(identity_id)
        if not assessment or assessment.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return assessment
