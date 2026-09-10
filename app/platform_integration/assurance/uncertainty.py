"""Cross-Phase Uncertainty Quantification Engine (Phase 5.58)."""

from dataclasses import dataclass
from typing import Dict, Any, List

from app.platform_integration.providers import PlatformProviderResult


@dataclass
class UncertaintyQuantification:
    overall_uncertainty: float
    missing_platforms: List[str]
    failing_platforms: List[str]
    stale_signals_factor: float


class CrossPhaseUncertaintyEngine:
    """Quantifies operational and systemic uncertainty during cross-phase integration."""

    def quantify_uncertainty(
        self,
        provider_results: Dict[str, PlatformProviderResult],
        all_expected_platforms: List[str],
    ) -> UncertaintyQuantification:
        missing = [p for p in all_expected_platforms if p not in provider_results]
        failing = [p for p, r in provider_results.items() if r.status != "SUCCESS"]

        missing_penalty = len(missing) * 0.15
        failing_penalty = len(failing) * 0.10

        provider_unc = [r.uncertainty for r in provider_results.values()]
        avg_prov_unc = (sum(provider_unc) / len(provider_unc)) if provider_unc else 0.5

        total_unc = round(min(1.0, avg_prov_unc + missing_penalty + failing_penalty), 3)

        return UncertaintyQuantification(
            overall_uncertainty=total_unc,
            missing_platforms=missing,
            failing_platforms=failing,
            stale_signals_factor=0.05 if failing else 0.0,
        )
