"""Service Health Assessment Subsystem (Phase 5.31)."""

import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class HealthState(str, Enum):
    HEALTHY = "HEALTHY"  # 90-100
    DEGRADED = "DEGRADED"  # 70-89
    UNHEALTHY = "UNHEALTHY"  # 40-69
    CRITICAL = "CRITICAL"  # <40


class HealthScore(BaseModel):
    overall_score: float  # 0.0 to 100.0
    state: HealthState
    latency_score: float = 100.0
    error_rate_score: float = 100.0
    saturation_score: float = 100.0


class ServiceHealth(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"hlth_{uuid.uuid4().hex[:12]}")
    service_id: str
    tenant_id: str
    score: HealthScore
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HealthAssessmentEngine:
    """Evaluates real-time service health based on operational metrics and SLIs."""

    def evaluate_health(
        self,
        service_id: str,
        tenant_id: str,
        latency_ms: float = 50.0,
        error_rate_pct: float = 0.0,
        saturation_pct: float = 20.0,
    ) -> ServiceHealth:
        # Calculate scores
        latency_score = max(0.0, 100.0 - max(0.0, latency_ms - 100.0) * 0.2)
        error_score = max(0.0, 100.0 - error_rate_pct * 10.0)
        saturation_score = max(0.0, 100.0 - max(0.0, saturation_pct - 80.0) * 2.0)

        overall = (latency_score * 0.4) + (error_score * 0.4) + (saturation_score * 0.2)

        if overall >= 90.0:
            state = HealthState.HEALTHY
        elif overall >= 70.0:
            state = HealthState.DEGRADED
        elif overall >= 40.0:
            state = HealthState.UNHEALTHY
        else:
            state = HealthState.CRITICAL

        hs = HealthScore(
            overall_score=round(overall, 2),
            state=state,
            latency_score=round(latency_score, 2),
            error_rate_score=round(error_score, 2),
            saturation_score=round(saturation_score, 2),
        )

        return ServiceHealth(
            service_id=service_id,
            tenant_id=tenant_id,
            score=hs,
        )
