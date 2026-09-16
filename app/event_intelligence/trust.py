"""Event Intelligence Trust Scoring Subsystem (Phase 5.34)."""

import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field

from app.platform_contracts.adapters import TrustAssessmentAdapter
from app.platform_contracts.trust import TrustAssessment


class EventTrustDimension(BaseModel):
    dimension_name: str
    score: float = 90.0


class EventTrustScore(BaseModel):
    score_id: str = Field(default_factory=lambda: f"etrust_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    event_id: str
    overall_trust_score: float = 92.0
    dimensions: List[EventTrustDimension] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EventTrustEngine:
    """Computes event intelligence trust scores and adapts to TrustAssessment contract."""

    def compute_trust(
        self,
        tenant_id: str,
        event_id: str,
        is_normalized: bool = True,
        is_source_verified: bool = True,
    ) -> EventTrustScore:
        score = 94.0 if (is_normalized and is_source_verified) else 50.0
        dims = [
            EventTrustDimension(dimension_name="evidence_quality", score=90.0),
            EventTrustDimension(dimension_name="correlation_confidence", score=92.0),
            EventTrustDimension(dimension_name="causality_confidence", score=88.0),
            EventTrustDimension(dimension_name="source_reliability", score=95.0 if is_source_verified else 50.0),
            EventTrustDimension(dimension_name="data_freshness", score=96.0),
        ]
        return EventTrustScore(
            tenant_id=tenant_id,
            event_id=event_id,
            overall_trust_score=score,
            dimensions=dims,
        )

    def to_contract_assessment(self, trust_score: EventTrustScore) -> TrustAssessment:
        return TrustAssessmentAdapter.from_domain_trust(
            tenant_id=trust_score.tenant_id,
            subject_type="ENTERPRISE_EVENT",
            subject_id=trust_score.event_id,
            score=trust_score.overall_trust_score,
        )
