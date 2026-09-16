"""Runtime health engine for Runtime Intelligence (Phase 5.57)."""

import logging
from typing import Any, Dict, Optional

from app.runtime_intelligence.models import RuntimeHealthAssessment, RuntimeHealthStatus
from app.runtime_intelligence.repositories import RuntimeHealthRepository

logger = logging.getLogger(__name__)


class RuntimeHealthEngine:
    """Evaluates multi-dimensional runtime system health across technical and operational telemetry."""

    def __init__(self, repo: RuntimeHealthRepository) -> None:
        self.repo = repo

    def evaluate_health(
        self,
        tenant_id: str,
        raw_metrics: Optional[Dict[str, Any]] = None,
        subsystem: str = "global",
    ) -> RuntimeHealthAssessment:
        metrics = raw_metrics or {}
        error_rate = float(metrics.get("error_rate", 0.001))
        latency = float(metrics.get("latency_p99_ms", metrics.get("latency_p99", metrics.get("p95_latency", 120.0))))
        cpu = float(metrics.get("cpu_utilization", metrics.get("cpu", 0.40)))
        sec_incidents = int(metrics.get("security_incidents", 0))

        dim_scores = {
            "availability": 1.0 if error_rate < 0.02 else (0.80 if error_rate < 0.05 else 0.40),
            "latency": 1.0 if latency < 200.0 else (0.80 if latency < 400.0 else 0.50),
            "error_rate": max(0.0, min(1.0, 1.0 - (error_rate * 10))),
            "resource_pressure": max(0.0, min(1.0, 1.0 - max(0.0, cpu - 0.70) * 3)),
            "security": 1.0 if sec_incidents == 0 else max(0.3, 1.0 - (sec_incidents * 0.2)),
            "policy": float(metrics.get("policy_compliance", 0.98)),
            "workflow": float(metrics.get("workflow_health", 0.96)),
            "model": float(metrics.get("model_health", 0.95)),
            "cost": 0.95 if metrics.get("cost_budget_pct", 50) < 90 else 0.75,
            "capacity": max(0.2, 1.0 - max(0.0, cpu - 0.80)),
            "trust": 0.96 if sec_incidents == 0 else 0.70,
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
            subsystem=subsystem,
        )
        self.repo.save(assessment)
        logger.info(f"Evaluated RuntimeHealth for '{subsystem}' (tenant: '{tenant_id}'): Status={status.value}, Score={avg_score:.4f}")
        return assessment
