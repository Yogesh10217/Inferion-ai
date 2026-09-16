"""Resilience Trust Scoring Subsystem (Phase 5.37)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_contracts.trust import TrustAssessment, TrustBand, TrustConfidence, TrustDimension


class ResilienceTrustDimension(str, Enum):
    RELIABILITY = "RELIABILITY"
    RECOVERABILITY = "RECOVERABILITY"
    AVAILABILITY_SLO = "AVAILABILITY_SLO"
    CAPACITY = "CAPACITY"
    FAILOVER_READINESS = "FAILOVER_READINESS"


class ResilienceTrustScore(BaseModel):
    score_id: str = Field(default_factory=lambda: f"restrust_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resource_id: str
    overall_score: float = 95.0
    band: TrustBand = TrustBand.HIGH_TRUST
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResilienceTrustEngine:
    """Resilience Trust Engine adapting scores cleanly to TrustAssessment platform contract."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()

    def calculate_resilience_trust(
        self,
        tenant_id: str,
        resource_id: str,
        successful_recoveries: int = 10,
        failed_recoveries: int = 0,
        slo_attainment_pct: float = 99.9,
    ) -> TrustAssessment:
        base_score = min(100.0, slo_attainment_pct)
        if failed_recoveries > 0:
            base_score -= (failed_recoveries * 15.0)

        score = max(0.0, min(100.0, base_score))

        band = TrustBand.HIGH_TRUST
        if score < 50.0:
            band = TrustBand.UNTRUSTED
        elif score < 70.0:
            band = TrustBand.RESTRICTED
        elif score < 90.0:
            band = TrustBand.TRUSTED

        dimensions = [
            TrustDimension(dimension_name="SLO_Attainment", score=slo_attainment_pct),
            TrustDimension(dimension_name="Recovery_Success_Rate", score=100.0 if failed_recoveries == 0 else 50.0),
        ]

        return TrustAssessment(
            subject_type="RESILIENCE_SERVICE",
            subject_id=resource_id,
            tenant_id=tenant_id,
            score=score,
            band=band,
            confidence=TrustConfidence.HIGH,
            dimensions=dimensions,
        )
