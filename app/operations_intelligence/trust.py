"""Operational Trust Intelligence (Phase 5.41)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.operations_intelligence.exceptions import CrossTenantOperationsAccessException
from app.platform_contracts.trust import TrustAssessment, TrustBand, TrustConfidence


class OperationalTrustScore(BaseModel):
    score_id: str = Field(default_factory=lambda: f"trust_op_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_service_id: str
    overall_score: float = 100.0
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationalTrustEngine:
    """Evaluates operational trust and adapts score to platform TrustAssessment."""

    def evaluate_trust(
        self,
        tenant_id: str,
        target_service_id: str,
        service_availability_pct: float = 99.9,
        incident_free_days: int = 30,
        recent_major_incidents_count: int = 0,
    ) -> TrustAssessment:
        incident_penalty = min(recent_major_incidents_count * 25.0, 60.0)
        base = min(service_availability_pct, 100.0)
        final_score = max(0.0, round(base - incident_penalty, 2))

        if final_score >= 90.0:
            band = TrustBand.HIGH_TRUST
        elif final_score >= 70.0:
            band = TrustBand.TRUSTED
        elif final_score >= 50.0:
            band = TrustBand.RESTRICTED
        else:
            band = TrustBand.UNTRUSTED

        assessment = TrustAssessment(
            subject_type="OPERATIONAL_SERVICE",
            subject_id=target_service_id,
            tenant_id=tenant_id,
            score=final_score,
            band=band,
            confidence=TrustConfidence.HIGH,
        )
        return assessment
