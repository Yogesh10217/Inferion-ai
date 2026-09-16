"""FinOps Trust Intelligence (Phase 5.42)."""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field

from app.platform_contracts.trust import TrustAssessment, TrustBand, TrustConfidence


class FinOpsTrustScore(BaseModel):
    score_id: str = Field(default_factory=lambda: f"trust_fin_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_entity: str
    overall_score: float = 100.0
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FinOpsTrustEngine:
    """Evaluates FinOps trust and adapts score to platform TrustAssessment."""

    def evaluate_trust(
        self,
        tenant_id: str,
        target_entity: str,
        budget_adherence_pct: float = 100.0,
        forecast_accuracy_pct: float = 95.0,
        unresolved_anomalies_count: int = 0,
    ) -> TrustAssessment:
        anomaly_penalty = min(unresolved_anomalies_count * 20.0, 50.0)
        base = (budget_adherence_pct + forecast_accuracy_pct) / 2.0
        final_score = max(0.0, round(base - anomaly_penalty, 2))

        if final_score >= 90.0:
            band = TrustBand.HIGH_TRUST
        elif final_score >= 70.0:
            band = TrustBand.TRUSTED
        elif final_score >= 50.0:
            band = TrustBand.RESTRICTED
        else:
            band = TrustBand.UNTRUSTED

        assessment = TrustAssessment(
            subject_type="FINOPS_INTELLIGENCE",
            subject_id=target_entity,
            tenant_id=tenant_id,
            score=final_score,
            band=band,
            confidence=TrustConfidence.HIGH,
        )
        return assessment
