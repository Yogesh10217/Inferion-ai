"""Output Quality Intelligence (Phase 5.44)."""

import logging
import hashlib
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException

logger = logging.getLogger(__name__)


class QualityDimension(str, Enum):
    CORRECTNESS = "CORRECTNESS"
    RELEVANCE = "RELEVANCE"
    CONSISTENCY = "CONSISTENCY"
    COMPLETENESS = "COMPLETENESS"
    GROUNDEDNESS = "GROUNDEDNESS"
    EXPLAINABILITY = "EXPLAINABILITY"


class QualityStatus(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    ACCEPTABLE = "ACCEPTABLE"
    POOR = "POOR"


class QualityScore(BaseModel):
    dimension: QualityDimension
    score: float  # 0.0 - 1.0
    weight: float = 1.0
    passed: bool = True


class QualityEvidence(BaseModel):
    evidence_id: str
    sample_hash: str
    sample_count: int = 50
    details: Dict[str, Any] = Field(default_factory=dict)


class ModelQualityAssessment(BaseModel):
    assessment_id: str
    model_id: str
    tenant_id: str
    overall_quality_score: float
    status: QualityStatus
    scores: List[QualityScore]
    evidence: QualityEvidence
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelQualityManager:
    """Manages model output quality intelligence."""

    def __init__(self) -> None:
        self._assessments: Dict[str, ModelQualityAssessment] = {}

    def evaluate_quality(
        self,
        model_id: str,
        tenant_id: str,
        scores: List[QualityScore],
        sample_count: int = 50,
    ) -> ModelQualityAssessment:
        overall = sum(s.score * s.weight for s in scores) / max(sum(s.weight for s in scores), 1.0)
        status = QualityStatus.EXCELLENT if overall >= 0.9 else (QualityStatus.GOOD if overall >= 0.75 else (QualityStatus.ACCEPTABLE if overall >= 0.6 else QualityStatus.POOR))

        ev_hash = hashlib.sha256(f"{model_id}:{tenant_id}:{overall}:{sample_count}".encode()).hexdigest()
        evidence = QualityEvidence(
            evidence_id=f"qevid-{uuid.uuid4().hex[:6]}",
            sample_hash=ev_hash,
            sample_count=sample_count,
        )

        assess_id = f"qassess-{uuid.uuid4().hex[:8]}"
        assessment = ModelQualityAssessment(
            assessment_id=assess_id,
            model_id=model_id,
            tenant_id=tenant_id,
            overall_quality_score=overall,
            status=status,
            scores=scores,
            evidence=evidence,
        )

        self._assessments[assess_id] = assessment
        logger.info(f"[MODEL QUALITY] Evaluated model {model_id} (Tenant: {tenant_id}) Score: {overall:.2f} Status: {status}")
        return assessment

    def get_latest_assessment(self, model_id: str, tenant_id: str) -> Optional[ModelQualityAssessment]:
        matches = [a for a in self._assessments.values() if a.model_id == model_id]
        if not matches:
            return None
        latest = matches[-1]
        if latest.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return latest
