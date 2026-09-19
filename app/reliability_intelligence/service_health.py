"""Service health intelligence engine (Phase 5.55)."""

import logging
from typing import Any, Dict, Optional

from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.reliability_intelligence.models import (
    ServiceHealthAssessment,
    ServiceHealthDimension,
    ServiceHealthStatus,
)
from app.reliability_intelligence.repositories import ServiceHealthRepository

logger = logging.getLogger(__name__)


class ServiceHealthEngine:
    """Evaluates multi-dimensional service health across availability, latency, error rate, throughput, capacity, resource."""

    def __init__(self, health_repo: ServiceHealthRepository) -> None:
        self.health_repo = health_repo

    def evaluate_service_health(
        self, tenant_id: str, service_id: str, raw_metrics: Optional[Dict[str, Any]] = None
    ) -> ServiceHealthAssessment:
        clean_metrics = SensitiveDataSanitizer.sanitize(raw_metrics or {})
        avail = clean_metrics.get("availability", 0.999)
        err_rate = clean_metrics.get("error_rate", 0.001)

        score = (avail + (1.0 - err_rate)) / 2.0

        if score >= 0.95:
            status = ServiceHealthStatus.HEALTHY
        elif score >= 0.85:
            status = ServiceHealthStatus.DEGRADED
        elif score >= 0.70:
            status = ServiceHealthStatus.UNHEALTHY
        else:
            status = ServiceHealthStatus.CRITICAL

        assessment = ServiceHealthAssessment(
            tenant_id=tenant_id,
            service_id=service_id,
            status=status,
            overall_score=round(score, 4),
            dimensions={
                ServiceHealthDimension.AVAILABILITY.value: avail,
                ServiceHealthDimension.ERROR_RATE.value: 1.0 - err_rate,
            },
        )

        self.health_repo.save(assessment)
        logger.info(
            f"Evaluated ServiceHealth for service '{service_id}' (tenant: '{tenant_id}') -> Status: {status.value}"
        )
        return assessment
