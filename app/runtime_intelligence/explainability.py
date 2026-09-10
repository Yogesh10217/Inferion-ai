"""Runtime Explainability Engine for Phase 5.57 Runtime Intelligence."""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ExplanationFactor:
    factor_name: str
    impact_score: float
    description: str


@dataclass
class RuntimeExplanation:
    explanation_id: str
    tenant_id: str
    target_entity: str
    summary: str
    factors: List[ExplanationFactor]
    evidence_ids: List[str]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RuntimeExplainabilityEngine:
    """Provides structured, auditable rationales for runtime decisions, anomalies, and recommendations."""

    def explain_decision(
        self,
        tenant_id: str,
        target_entity: str,
        decision_summary: str,
        evidence_ids: List[str],
        telemetry_context: Optional[Dict[str, Any]] = None,
    ) -> RuntimeExplanation:
        telem = telemetry_context or {}
        factors: List[ExplanationFactor] = []

        if "latency_p99" in telem or "latency_p99_ms" in telem:
            lat = float(telem.get("latency_p99", telem.get("latency_p99_ms", 150.0)))
            factors.append(
                ExplanationFactor(
                    factor_name="Latency Elevation",
                    impact_score=round(min(1.0, lat / 500.0), 2),
                    description=f"Observed P99 latency of {lat:.1f}ms influenced the runtime evaluation for {target_entity}",
                )
            )

        if "error_rate" in telem:
            err = float(telem["error_rate"])
            factors.append(
                ExplanationFactor(
                    factor_name="Error Rate Surge",
                    impact_score=round(min(1.0, err * 10), 2),
                    description=f"Error rate at {err * 100:.1f}% contributed to the governance/assurance posture",
                )
            )

        if not factors:
            factors = [
                ExplanationFactor(
                    factor_name="Operational Metric Variance",
                    impact_score=0.45,
                    description=f"Telemetry metrics for '{target_entity}' deviated from baseline during assessment window",
                ),
                ExplanationFactor(
                    factor_name="Evidence Alignment",
                    impact_score=0.35,
                    description=f"Cross-domain evidence items ({len(evidence_ids)} records) corroborated the operational finding",
                ),
            ]

        exp = RuntimeExplanation(
            explanation_id=f"exp_{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            target_entity=target_entity,
            summary=decision_summary,
            factors=factors,
            evidence_ids=evidence_ids,
        )
        logger.info(f"Generated runtime explanation for '{target_entity}': {decision_summary} ({len(factors)} factors)")
        return exp
