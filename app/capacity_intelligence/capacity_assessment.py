"""Capacity assessment engine for Capacity Intelligence (Phase 5.56)."""

import logging

from app.capacity_intelligence.models import CapacityAssessment, CapacityStatus
from app.capacity_intelligence.repositories import CapacityAssessmentRepository

logger = logging.getLogger(__name__)


class CapacityAssessmentEngine:
    """Evaluates resource capacity status, consumed percentage, and headroom."""

    def __init__(self, repo: CapacityAssessmentRepository) -> None:
        self.repo = repo

    def assess_capacity(self, tenant_id: str, resource_id: str, consumed_pct: float = 65.0) -> CapacityAssessment:
        headroom = max(0.0, 100.0 - consumed_pct)
        risk_score = round(consumed_pct / 100.0, 4)

        if consumed_pct >= 90.0:
            status = CapacityStatus.CRITICAL
        elif consumed_pct >= 80.0:
            status = CapacityStatus.SATURATED
        elif consumed_pct >= 70.0:
            status = CapacityStatus.CONSTRAINED
        elif consumed_pct >= 55.0:
            status = CapacityStatus.WATCH
        else:
            status = CapacityStatus.HEALTHY

        assessment = CapacityAssessment(
            tenant_id=tenant_id,
            resource_id=resource_id,
            status=status,
            consumed_percentage=consumed_pct,
            headroom_percentage=headroom,
            saturation_risk_score=risk_score,
        )
        self.repo.save(assessment)
        logger.info(
            f"Evaluated CapacityAssessment for resource '{resource_id}': Status={status.value}, Consumed={consumed_pct}%"
        )
        return assessment
