"""Continuous drift detection engine for Continuous Assurance (Phase 5.54)."""

import logging
from typing import Any, Dict

from app.continuous_assurance.models import (
    AssuranceDrift,
    DriftSeverity,
    DriftStatus,
    DriftType,
)
from app.continuous_assurance.repositories import DriftRepository

logger = logging.getLogger(__name__)


class ContinuousDriftDetectionEngine:
    """Detects multi-dimensional drift across policy, risk, trust, control, configuration, behavior, and runtime."""

    def __init__(self, drift_repo: DriftRepository) -> None:
        self.drift_repo = drift_repo

    def analyze_drift(
        self,
        tenant_id: str,
        drift_type_str: str,
        expected_state: Dict[str, Any],
        observed_state: Dict[str, Any],
    ) -> AssuranceDrift:
        try:
            d_type = DriftType(drift_type_str.upper())
        except ValueError:
            d_type = DriftType.RUNTIME

        diffs = []
        for k in set(list(expected_state.keys()) + list(observed_state.keys())):
            exp_val = expected_state.get(k)
            obs_val = observed_state.get(k)
            if exp_val != obs_val:
                diffs.append(f"{k}: expected '{exp_val}', observed '{obs_val}'")

        if diffs:
            summary = "; ".join(diffs)
            severity = DriftSeverity.HIGH if len(diffs) > 2 else DriftSeverity.MEDIUM
        else:
            summary = "No drift detected between expected and observed state"
            severity = DriftSeverity.LOW

        drift = AssuranceDrift(
            tenant_id=tenant_id,
            drift_type=d_type,
            severity=severity,
            expected_state=expected_state,
            observed_state=observed_state,
            difference_summary=summary,
            confidence=0.96,
            status=DriftStatus.DETECTED,
            evidence_references=[f"ev_drift_{tenant_id}_01"],
        )

        self.drift_repo.save(drift)
        logger.info(
            f"Analyzed drift '{drift.drift_id}' for tenant '{tenant_id}' -> Type: {d_type.value}, Summary: {summary}"
        )
        return drift
