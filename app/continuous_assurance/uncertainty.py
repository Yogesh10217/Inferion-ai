"""Uncertainty intelligence engine for Continuous Assurance (Phase 5.54)."""

from typing import Dict, Any, List

class UncertaintyCategory:
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
    STALE_DATA = "STALE_DATA"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    LOW_SOURCE_RELIABILITY = "LOW_SOURCE_RELIABILITY"
    INCOMPLETE_COVERAGE = "INCOMPLETE_COVERAGE"
    HIGH_RUNTIME_VARIABILITY = "HIGH_RUNTIME_VARIABILITY"


class ContinuousAssuranceUncertaintyAssessment:
    """Assesses data uncertainty and conflicting signals in continuous observations."""

    def assess_uncertainty(self, observation_count: int) -> Dict[str, Any]:
        categories = []
        if observation_count < 3:
            categories.append(UncertaintyCategory.INSUFFICIENT_DATA)

        uncertainty_level = "HIGH" if categories else "LOW"

        return {
            "uncertainty_level": uncertainty_level,
            "categories": categories,
            "observation_count": observation_count,
        }
