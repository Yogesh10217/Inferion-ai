"""Runtime drift detector for Runtime Intelligence (Phase 5.57)."""

import logging
from typing import Any, Dict

from app.runtime_intelligence.models import RuntimeDrift, RuntimeDriftSeverity

logger = logging.getLogger(__name__)


class RuntimeDriftDetector:
    """Detects runtime behavioral, configuration, policy, and model drift."""

    def analyze_drift(
        self,
        tenant_id: str,
        drift_type: str,
        expected_state: Dict[str, Any],
        actual_state: Dict[str, Any],
    ) -> RuntimeDrift:
        diff_keys = [k for k in expected_state if expected_state.get(k) != actual_state.get(k)]
        if not diff_keys:
            severity = RuntimeDriftSeverity.NONE
            summary = "No drift detected between expected and actual state"
        elif len(diff_keys) > 3:
            severity = RuntimeDriftSeverity.HIGH
            summary = f"Multiple drift points detected: {', '.join(diff_keys)}"
        else:
            severity = RuntimeDriftSeverity.MODERATE
            summary = f"Minor drift detected on keys: {', '.join(diff_keys)}"

        drift = RuntimeDrift(
            tenant_id=tenant_id,
            drift_type=drift_type,
            severity=severity,
            expected_state=expected_state,
            actual_state=actual_state,
            difference_summary=summary,
        )
        logger.info(f"Analyzed RuntimeDrift '{drift.drift_id}' (Type: {drift_type}, Sev: {severity.value})")
        return drift
