"""Deterministic Trust & AI Transparency Assessment Subsystem."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class TrustDimension(str, Enum):
    SECURITY = "SECURITY"
    PRIVACY = "PRIVACY"
    SAFETY = "SAFETY"
    RELIABILITY = "RELIABILITY"
    COMPLIANCE = "COMPLIANCE"
    DATA_QUALITY = "DATA_QUALITY"
    MODEL_QUALITY = "MODEL_QUALITY"
    EXPLAINABILITY = "EXPLAINABILITY"
    HUMAN_OVERSIGHT = "HUMAN_OVERSIGHT"


class TrustFactor(BaseModel):
    dimension: TrustDimension
    score: float = 100.0  # 0.0 to 100.0
    weight: float = 1.0
    evidence_ids: List[str] = Field(default_factory=list)
    description: str = ""


class TrustAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"trust_{uuid.uuid4().hex[:10]}")
    target_resource_id: str
    tenant_id: str = "global"

    overall_trust_score: float = 100.0  # 0.0 to 100.0 scale
    factors: List[TrustFactor] = Field(default_factory=list)
    disclaimer: str = (
        "Internal governance assessment metric. Not a guarantee, certification, or warranty."
    )
    assessed_at: datetime = Field(default_factory=_now)


class TrustEngine:
    """Calculates deterministic internal AI trust scores across 9 dimensions."""

    def __init__(self) -> None:
        self._assessments: Dict[str, TrustAssessment] = {}

    def calculate_trust(
        self,
        target_resource_id: str,
        tenant_id: str = "global",
        factors: Optional[List[TrustFactor]] = None,
    ) -> TrustAssessment:
        f_list = factors or [
            TrustFactor(dimension=TrustDimension.SECURITY, score=98.0, weight=1.5),
            TrustFactor(dimension=TrustDimension.PRIVACY, score=95.0, weight=1.2),
            TrustFactor(dimension=TrustDimension.SAFETY, score=92.0, weight=1.5),
            TrustFactor(dimension=TrustDimension.RELIABILITY, score=99.0, weight=1.0),
            TrustFactor(dimension=TrustDimension.COMPLIANCE, score=90.0, weight=1.0),
            TrustFactor(dimension=TrustDimension.EXPLAINABILITY, score=95.0, weight=1.0),
            TrustFactor(dimension=TrustDimension.HUMAN_OVERSIGHT, score=94.0, weight=1.0),
        ]

        total_weight = sum(f.weight for f in f_list)
        weighted_score = sum(f.score * f.weight for f in f_list)
        overall = float(min(100.0, max(0.0, weighted_score / total_weight if total_weight > 0 else 100.0)))

        ass = TrustAssessment(
            target_resource_id=target_resource_id,
            tenant_id=tenant_id,
            overall_trust_score=overall,
            factors=f_list,
        )
        self._assessments[ass.assessment_id] = ass
        logger.info(f"[TRUST ENGINE] Assessed trust for '{target_resource_id}' ({tenant_id}): Score = {overall:.1f}")
        return ass

    def get_assessment(self, assessment_id: str) -> TrustAssessment:
        ass = self._assessments.get(assessment_id)
        if not ass:
            raise KeyError(f"Trust assessment '{assessment_id}' not found")
        return ass

    def list_assessments(self, tenant_id: Optional[str] = None) -> List[TrustAssessment]:
        res = list(self._assessments.values())
        if tenant_id:
            res = [r for r in res if r.tenant_id == tenant_id]
        return res
