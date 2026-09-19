"""Reliability Trust Engine Subsystem (Phase 5.31)."""

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.platform_contracts.adapters import TrustAssessmentAdapter
from app.platform_contracts.trust import TrustAssessment


class ReliabilityTrustScore(BaseModel):
    service_id: str
    tenant_id: str
    score: float  # 0.0 to 100.0
    slo_compliance_score: float = 95.0
    mean_time_between_failures_score: float = 90.0
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReliabilityTrustEngine:
    """Computes service reliability trust scores and adapts to TrustAssessment contract."""

    def compute_trust_score(
        self, tenant_id: str, service_id: str, slo_achievement_pct: float = 99.5
    ) -> ReliabilityTrustScore:
        score = min(100.0, slo_achievement_pct)
        return ReliabilityTrustScore(
            tenant_id=tenant_id,
            service_id=service_id,
            score=round(score, 2),
        )

    def to_contract_assessment(self, trust_score: ReliabilityTrustScore) -> TrustAssessment:
        return TrustAssessmentAdapter.from_domain_trust(
            tenant_id=trust_score.tenant_id,
            subject_type="RELIABILITY_SERVICE",
            subject_id=trust_score.service_id,
            score=trust_score.score,
        )
