"""Dynamic Weighted Cross-Phase Assurance Engine (Phase 5.58)."""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from app.platform_integration.models import PlatformAssurancePosture
from app.platform_integration.providers import PlatformProviderResult

logger = logging.getLogger(__name__)


@dataclass
class AssuranceWeightPolicy:
    """Configurable baseline weights per platform domain."""
    base_weights: Dict[str, float] = field(
        default_factory=lambda: {
            "RUNTIME": 1.2,
            "CAPACITY": 1.0,
            "RELIABILITY": 1.3,
            "CONTINUOUS_ASSURANCE": 1.2,
            "AUTONOMOUS_ASSURANCE": 1.1,
            "DECISION_INTELLIGENCE": 1.0,
            "UNIFIED_INTELLIGENCE": 1.2,
            "SECURITY": 1.4,
            "OPERATIONS": 1.0,
        }
    )

    def calculate_effective_weight(
        self,
        platform: str,
        confidence: float,
        provider_status: str,
        freshness_factor: float = 1.0,
    ) -> float:
        base = self.base_weights.get(platform.upper(), 1.0)
        health_factor = 1.0 if provider_status == "SUCCESS" else (0.5 if provider_status == "DEGRADED" else 0.1)
        return round(base * max(0.1, confidence) * freshness_factor * health_factor, 4)


class CrossPhaseAssuranceEngine:
    """Synthesizes dynamic, explainable cross-phase assurance postures across all upper intelligence layers."""

    def __init__(self, policy: Optional[AssuranceWeightPolicy] = None) -> None:
        self.policy = policy or AssuranceWeightPolicy()

    def evaluate_assurance_posture(
        self,
        tenant_id: str,
        provider_results: Dict[str, PlatformProviderResult],
    ) -> PlatformAssurancePosture:
        effective_weights: Dict[str, float] = {}
        platform_scores: Dict[str, float] = {}
        degraded: List[str] = []
        confidences: List[float] = []
        uncertainties: List[float] = []

        for p_name, res in provider_results.items():
            confidences.append(res.confidence)
            uncertainties.append(res.uncertainty)

            score = float(res.data.get("score", 0.0))
            platform_scores[p_name] = score

            if res.status != "SUCCESS" or score < 0.75:
                degraded.append(p_name)

            w = self.policy.calculate_effective_weight(p_name, res.confidence, res.status)
            effective_weights[p_name] = w

        total_weight = sum(effective_weights.values())
        if total_weight > 0:
            overall_score = sum(platform_scores[p] * effective_weights[p] for p in platform_scores) / total_weight
        else:
            overall_score = 0.5

        overall_score = round(max(0.0, min(1.0, overall_score)), 3)
        avg_confidence = round(sum(confidences) / len(confidences), 3) if confidences else 0.8
        avg_uncertainty = round(sum(uncertainties) / len(uncertainties), 3) if uncertainties else 0.2

        trust_band = self._score_to_trust_band(overall_score)
        posture = self._score_to_posture(overall_score, degraded)

        return PlatformAssurancePosture(
            tenant_id=tenant_id,
            overall_score=overall_score,
            confidence=avg_confidence,
            uncertainty=avg_uncertainty,
            trust_band=trust_band,
            posture=posture,
            degraded_platforms=degraded,
            platform_scores=platform_scores,
            effective_weights=effective_weights,
            critical_dependencies=["CAPACITY", "RELIABILITY"] if "RUNTIME" in degraded else [],
        )

    def _score_to_trust_band(self, score: float) -> str:
        if score >= 0.9:
            return "HIGH_TRUST"
        if score >= 0.7:
            return "TRUSTED"
        if score >= 0.5:
            return "RESTRICTED"
        return "UNTRUSTED"

    def _score_to_posture(self, score: float, degraded_platforms: List[str]) -> str:
        if len(degraded_platforms) >= 3 or score < 0.5:
            return "COMPROMISED"
        if len(degraded_platforms) >= 1 or score < 0.75:
            return "DEGRADED"
        if score < 0.88:
            return "WATCH"
        return "ASSURED"
