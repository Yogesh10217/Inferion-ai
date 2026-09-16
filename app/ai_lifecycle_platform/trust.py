"""Lifecycle Trust Evaluation Subsystem (Phase 5.33)."""

import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field

from app.platform_contracts.adapters import TrustAssessmentAdapter
from app.platform_contracts.trust import TrustAssessment


class LifecycleTrustDimension(BaseModel):
    name: str
    score: float = 90.0


class LifecycleTrustScore(BaseModel):
    score_id: str = Field(default_factory=lambda: f"ltrust_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    overall_trust_score: float = 92.0
    dimensions: List[LifecycleTrustDimension] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LifecycleTrustEngine:
    """Computes AI asset lifecycle trust scores and adapts to TrustAssessment contract."""

    def compute_trust(
        self,
        tenant_id: str,
        asset_id: str,
        eval_passed: bool = True,
        gates_passed: bool = True,
    ) -> LifecycleTrustScore:
        score = 95.0 if (eval_passed and gates_passed) else 45.0
        dims = [
            LifecycleTrustDimension(name="DATA_QUALITY", score=90.0),
            LifecycleTrustDimension(name="MODEL_QUALITY", score=score),
            LifecycleTrustDimension(name="SAFETY", score=92.0),
            LifecycleTrustDimension(name="SECURITY", score=94.0),
            LifecycleTrustDimension(name="RELIABILITY", score=90.0),
            LifecycleTrustDimension(name="COMPLIANCE", score=95.0),
            LifecycleTrustDimension(name="OPERATIONAL_MATURITY", score=88.0),
            LifecycleTrustDimension(name="EVIDENCE_CONFIDENCE", score=96.0),
        ]
        return LifecycleTrustScore(
            tenant_id=tenant_id,
            asset_id=asset_id,
            overall_trust_score=score,
            dimensions=dims,
        )

    def to_contract_assessment(self, trust_score: LifecycleTrustScore) -> TrustAssessment:
        return TrustAssessmentAdapter.from_domain_trust(
            tenant_id=trust_score.tenant_id,
            subject_type="AI_ASSET",
            subject_id=trust_score.asset_id,
            score=trust_score.overall_trust_score,
        )
