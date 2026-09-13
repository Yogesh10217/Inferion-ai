"""
Deployment Health Correlation Module for Phase 5.68.
Correlates deployment identity, artifact digest, progressive traffic %, SLOs, error budgets, and incidents into a unified health score.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer
from app.operations.error_budget import ErrorBudgetResult, ErrorBudgetStatus
from app.operations.incident_management import Incident
from app.operations.observability_engine import ObservationResult
from app.operations.slo import SLOResult, SLOStatus


@dataclass
class DeploymentHealthResult:
    deployment_identity: str
    artifact_digest: str
    release_candidate_id: str
    traffic_percentage: float
    is_healthy: bool
    health_score: float
    evidence_level: str
    slo_status_summary: Dict[str, int]
    error_budget_status: str
    active_incident_count: int
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "deployment_identity": self.deployment_identity,
            "artifact_digest": self.artifact_digest,
            "release_candidate_id": self.release_candidate_id,
            "traffic_percentage": self.traffic_percentage,
            "is_healthy": self.is_healthy,
            "health_score": self.health_score,
            "evidence_level": self.evidence_level,
            "slo_status_summary": self.slo_status_summary,
            "error_budget_status": self.error_budget_status,
            "active_incident_count": self.active_incident_count,
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class DeploymentHealthCorrelator:
    """Correlates post-deployment telemetry signals with candidate deployment metadata."""

    def correlate(
        self,
        deployment_identity: str,
        artifact_digest: str,
        release_candidate_id: str,
        traffic_percentage: float,
        observation: ObservationResult,
        slo_results: List[SLOResult],
        error_budget_result: Optional[ErrorBudgetResult],
        incidents: List[Incident],
    ) -> DeploymentHealthResult:
        slo_counts = {
            "MET": sum(1 for s in slo_results if s.status == SLOStatus.MET),
            "AT_RISK": sum(1 for s in slo_results if s.status == SLOStatus.AT_RISK),
            "BREACHED": sum(1 for s in slo_results if s.status == SLOStatus.BREACHED),
        }

        eb_status = error_budget_result.status.value if error_budget_result else "NOT_ENOUGH_DATA"
        active_inc = len([i for i in incidents if i.state.value not in ("RESOLVED", "CLOSED")])

        # Compute health score (0.0 to 100.0)
        base_score = 100.0
        if slo_counts["BREACHED"] > 0:
            base_score -= 30.0 * slo_counts["BREACHED"]
        if slo_counts["AT_RISK"] > 0:
            base_score -= 10.0 * slo_counts["AT_RISK"]
        if eb_status == "EXHAUSTED":
            base_score -= 40.0
        elif eb_status == "CRITICAL":
            base_score -= 20.0
        if active_inc > 0:
            base_score -= 25.0 * active_inc

        final_score = max(0.0, min(100.0, base_score))
        is_healthy = final_score >= 70.0 and slo_counts["BREACHED"] == 0 and active_inc == 0

        return DeploymentHealthResult(
            deployment_identity=deployment_identity,
            artifact_digest=artifact_digest,
            release_candidate_id=release_candidate_id,
            traffic_percentage=traffic_percentage,
            is_healthy=is_healthy,
            health_score=final_score,
            evidence_level=observation.evidence_level,
            slo_status_summary=slo_counts,
            error_budget_status=eb_status,
            active_incident_count=active_inc,
            details={
                "observation_status": observation.status.value,
                "application_metrics": observation.application_metrics,
            },
        )
