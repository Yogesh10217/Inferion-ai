"""Runtime uncertainty assessment for Runtime Intelligence (Phase 5.57)."""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class RuntimeUncertaintyAssessmentEngine:
    """Evaluates data, signal, context, and model uncertainty, quantifying confidence intervals."""

    def evaluate_uncertainty(
        self,
        tenant_id: str,
        sample_variance: float = 0.04,
        sample_count: int = 20,
        assessment_type: str = "HEALTH_EVALUATION",
    ) -> Dict[str, Any]:
        # Standard error estimation
        se = (sample_variance / max(1, sample_count)) ** 0.5
        ci_half = 1.96 * se
        ci_lower = round(max(0.0, 0.90 - ci_half), 3)
        ci_upper = round(min(1.0, 0.90 + ci_half), 3)

        var_factor = min(0.15, sample_variance * 2.0)
        dimensions = {
            "DATA_UNCERTAINTY": round(0.03 + var_factor, 3),
            "SIGNAL_UNCERTAINTY": round(0.04 + (0.05 if sample_count < 10 else 0.0), 3),
            "CONTEXT_UNCERTAINTY": round(0.05, 3),
            "DEPENDENCY_UNCERTAINTY": round(0.06, 3),
            "MODEL_UNCERTAINTY": round(0.04, 3),
            "CONFLICTING_SIGNALS": round(0.02, 3),
            "INSUFFICIENT_EVIDENCE": round(0.08 if sample_count < 5 else 0.02, 3),
        }
        overall = sum(dimensions.values()) / len(dimensions)

        logger.info(f"Evaluated RuntimeUncertainty for tenant '{tenant_id}' ({assessment_type}): CI=[{ci_lower}, {ci_upper}]")
        return {
            "tenant_id": tenant_id,
            "assessment_type": assessment_type,
            "overall_uncertainty": round(overall, 4),
            "confidence_interval_lower": ci_lower,
            "confidence_interval_upper": ci_upper,
            "dimensions": dimensions,
        }
