"""Integration Trust Evaluation (Phase 5.40)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import CrossTenantIntegrationAccessException
from app.platform_contracts.trust import TrustAssessment, TrustBand, TrustConfidence


class IntegrationTrustDimension(str, Enum):
    CONNECTOR_RELIABILITY = "CONNECTOR_RELIABILITY"
    VERIFICATION_SUCCESS = "VERIFICATION_SUCCESS"
    FAILURE_HISTORY = "FAILURE_HISTORY"
    SECURITY_POSTURE = "SECURITY_POSTURE"
    EVIDENCE_INTEGRITY = "EVIDENCE_INTEGRITY"


class IntegrationTrustScore(BaseModel):
    score_id: str = Field(default_factory=lambda: f"trust_int_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_id: str
    overall_score: float = 100.0
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrationTrustEngine:
    """Evaluates integration trust and adapts score to platform TrustAssessment."""

    def evaluate_trust(
        self,
        tenant_id: str,
        target_id: str,
        connector_reliability_score: float = 100.0,
        verification_success_score: float = 100.0,
        security_posture_score: float = 100.0,
        evidence_integrity_score: float = 100.0,
        recent_failures_count: int = 0,
    ) -> TrustAssessment:
        failure_penalty = min(recent_failures_count * 15.0, 50.0)
        base = (connector_reliability_score + verification_success_score + security_posture_score + evidence_integrity_score) / 4.0
        final_score = max(0.0, round(base - failure_penalty, 2))

        if final_score >= 90.0:
            band = TrustBand.HIGH_TRUST
        elif final_score >= 70.0:
            band = TrustBand.TRUSTED
        elif final_score >= 50.0:
            band = TrustBand.RESTRICTED
        else:
            band = TrustBand.UNTRUSTED

        assessment = TrustAssessment(
            subject_type="INTEGRATION_CONNECTOR",
            subject_id=target_id,
            tenant_id=tenant_id,
            score=final_score,
            band=band,
            confidence=TrustConfidence.HIGH,
        )
        return assessment
