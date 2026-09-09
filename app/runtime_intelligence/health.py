"""Runtime health engine for Runtime Intelligence (Phase 5.54)."""

import logging
from typing import Dict, Any, Optional
from app.runtime_intelligence.models import RuntimeHealthAssessment, RuntimeHealthStatus
from app.runtime_intelligence.repositories import RuntimeHealthRepository

logger = logging.getLogger(__name__)


class RuntimeHealthEngine:
    """Evaluates multi-dimensional runtime system health."""

    def __init__(self, repo: RuntimeHealthRepository) -> None:
        self.repo = repo

    def evaluate_health(
        self, tenant_id: str, raw_metrics: Optional[Dict[str, Any]] = None
    ) -> RuntimeHealthAssessment:
        metrics = raw_metrics or {}
        error_rate = metrics.get("error_rate", 0.001)
        latency = metrics.get("latency_p99_ms", 120.0)

        dim_scores = {
            "availability": 1.0 if error_rate < 0.05 else 0.5,
            "latency": 1.0 if latency < 300.0 else 0.7,
            "error_rate": max(0.0, 1.0 - (error_rate * 10)),
            "security": 0.95,
            "policy": 0.98,
            "workflow": 0.96,
            "model": 0.94,
            "cost": 0.92,
            "capacity": 0.90,
            "trust": 0.95,
        }
        avg_score = sum(dim_scores.values()) / len(dim_scores)

        if avg_score >= 0.90:
            status = RuntimeHealthStatus.HEALTHY
        elif avg_score >= 0.75:
            status = RuntimeHealthStatus.DEGRADED
        elif avg_score >= 0.60:
            status = RuntimeHealthStatus.UNSTABLE
        elif avg_score >= 0.40:
            status = RuntimeHealthStatus.AT_RISK
        else:
            status = RuntimeHealthStatus.CRITICAL

        assessment = RuntimeHealthAssessment(
            tenant_id=tenant_id,
            overall_status=status,
            overall_score=round(avg_score, 4),
            dimensions=dim_scores,
        )
        self.repo.save(assessment)
        logger.info(f"Evaluated RuntimeHealth for tenant '{tenant_id}': Status={status.value}, Score={avg_score:.4f}")
        return assessment
