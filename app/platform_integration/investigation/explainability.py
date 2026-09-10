"""Explainability Engine for Cross-Phase Inferences (Phase 5.58)."""

from typing import Dict, Any, List

from app.platform_integration.models import (
    CrossPhaseCorrelation,
    CrossPhaseRecommendation,
    PlatformAssurancePosture,
)


class PlatformIntegrationExplainabilityEngine:
    """Produces structured, audit-ready explanations for cross-phase operations."""

    def explain_correlation(self, correlation: CrossPhaseCorrelation) -> Dict[str, Any]:
        return {
            "correlation_id": correlation.correlation_id,
            "source_platforms": [p.value for p in correlation.source_platforms],
            "strength": correlation.correlation_strength,
            "is_causal": correlation.is_causal,
            "causal_status": correlation.causal_status.value,
            "reason": correlation.explanation,
            "evidence_count": len(correlation.evidence_references),
        }

    def explain_posture(self, posture: PlatformAssurancePosture) -> Dict[str, Any]:
        return {
            "overall_score": posture.overall_score,
            "trust_band": posture.trust_band,
            "posture": posture.posture,
            "degraded_platforms": posture.degraded_platforms,
            "effective_weights": posture.effective_weights,
            "critical_dependencies": posture.critical_dependencies,
        }
