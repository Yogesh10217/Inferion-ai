"""Continuous Model Assurance Platform (Phase 5.44)."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException, ModelAssuranceException

logger = logging.getLogger(__name__)


class AssuranceDimension(str, Enum):
    PERFORMANCE = "PERFORMANCE"
    SAFETY = "SAFETY"
    SECURITY = "SECURITY"
    GOVERNANCE = "GOVERNANCE"
    RELIABILITY = "RELIABILITY"
    COMPLIANCE = "COMPLIANCE"


class AssuranceStatus(str, Enum):
    ASSURED = "ASSURED"
    WARNING = "WARNING"
    UNASSURED = "UNASSURED"


class ModelAssuranceScore(BaseModel):
    dimension: AssuranceDimension
    score: float  # 0.0 - 1.0
    weight: float = 1.0
    passed: bool = True


class AssuranceAssessment(BaseModel):
    assessment_id: str
    model_id: str
    tenant_id: str
    overall_assurance_score: float  # 0.0 - 1.0
    status: AssuranceStatus = AssuranceStatus.ASSURED
    scores: List[ModelAssuranceScore] = Field(default_factory=list)
    control_assurance_ref: Optional[str] = None
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelAssuranceManager:
    """Manages continuous model assurance integration with control_assurance."""

    def __init__(self) -> None:
        self._assessments: Dict[str, AssuranceAssessment] = {}

    def compute_assurance(
        self,
        model_id: str,
        tenant_id: str,
        scores: List[ModelAssuranceScore],
        control_assurance_ref: Optional[str] = None,
    ) -> AssuranceAssessment:
        overall = sum(s.score * s.weight for s in scores) / max(sum(s.weight for s in scores), 1.0)
        status = (
            AssuranceStatus.ASSURED
            if overall >= 0.85
            else (AssuranceStatus.WARNING if overall >= 0.7 else AssuranceStatus.UNASSURED)
        )

        assess = AssuranceAssessment(
            assessment_id=f"assr-{uuid.uuid4().hex[:8]}",
            model_id=model_id,
            tenant_id=tenant_id,
            overall_assurance_score=overall,
            status=status,
            scores=scores,
            control_assurance_ref=control_assurance_ref,
        )

        self._assessments[model_id] = assess
        logger.info(
            f"[MODEL ASSURANCE] Computed assurance for model {model_id} (Tenant: {tenant_id}) Score: {overall:.2f} Status: {status}"
        )
        return assess

    def get_latest_assurance(self, model_id: str, tenant_id: str) -> AssuranceAssessment:
        assess = self._assessments.get(model_id)
        if not assess:
            raise ModelAssuranceException(f"No assurance record for model '{model_id}'.")
        if assess.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return assess
