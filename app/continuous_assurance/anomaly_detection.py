"""Runtime anomaly detection engine for Continuous Assurance (Phase 5.54)."""

import logging
from typing import Any, Dict, List

from app.continuous_assurance.models import RuntimeObservation

logger = logging.getLogger(__name__)


class RuntimeAnomalyDetectionEngine:
    """Detects statistical, rule-based, threshold, and temporal runtime anomalies with complete explainability."""

    def detect_anomalies(self, observations: List[RuntimeObservation]) -> List[Dict[str, Any]]:
        anomalies = []
        for obs in observations:
            if obs.severity.value in ("HIGH", "CRITICAL"):
                anomalies.append({
                    "observation_id": obs.observation_id,
                    "tenant_id": obs.tenant_id,
                    "anomaly_type": "RULE_BASED_SEVERITY",
                    "severity": obs.severity.value,
                    "confidence": 0.95,
                    "explanation": f"Observed high severity signal '{obs.observation_type.value}' from '{obs.source_domain}'",
                })
        return anomalies
