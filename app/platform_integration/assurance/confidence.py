"""Cross-Phase Confidence Assessment Engine (Phase 5.58)."""

from dataclasses import dataclass
from typing import Dict

from app.platform_integration.providers import PlatformProviderResult


@dataclass
class ConfidenceAssessment:
    overall_confidence: float
    provider_confidence: float
    evidence_confidence: float
    completeness_confidence: float
    sample_consistency: float


class CrossPhaseConfidenceEngine:
    """Calculates multidimensional confidence for cross-phase operations."""

    def evaluate_confidence(
        self,
        provider_results: Dict[str, PlatformProviderResult],
        evidence_count: int,
        expected_platforms_count: int = 7,
    ) -> ConfidenceAssessment:
        if not provider_results:
            return ConfidenceAssessment(0.0, 0.0, 0.0, 0.0, 0.0)

        prov_confs = [r.confidence for r in provider_results.values()]
        avg_prov = sum(prov_confs) / len(prov_confs)

        # Completeness based on active providers
        completeness = min(1.0, len(provider_results) / max(1, expected_platforms_count))

        # Evidence confidence scales with corroborated evidence references
        ev_conf = min(1.0, 0.5 + (evidence_count * 0.1))

        # Consistency based on variance of scores
        scores = [float(r.data.get("score", 0.8)) for r in provider_results.values() if r.status == "SUCCESS"]
        if len(scores) > 1:
            mean = sum(scores) / len(scores)
            var = sum((s - mean) ** 2 for s in scores) / len(scores)
            consistency = max(0.2, 1.0 - var)
        else:
            consistency = 0.9

        overall = round((avg_prov * 0.35) + (completeness * 0.25) + (ev_conf * 0.2) + (consistency * 0.2), 3)

        return ConfidenceAssessment(
            overall_confidence=overall,
            provider_confidence=round(avg_prov, 3),
            evidence_confidence=round(ev_conf, 3),
            completeness_confidence=round(completeness, 3),
            sample_consistency=round(consistency, 3),
        )
