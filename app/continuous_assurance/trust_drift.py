"""Trust drift analyzer for Continuous Assurance (Phase 5.54)."""

import logging
from typing import Dict, Any
from app.continuous_assurance.models import AssuranceDrift, DriftType, DriftSeverity, DriftStatus

logger = logging.getLogger(__name__)


class TrustDriftAnalyzer:
    """Analyzes trust score degradation across security, identity, workflow, model, and decisions."""

    def analyze_trust_drift(
        self, tenant_id: str, expected_trust: float, observed_trust: float
    ) -> AssuranceDrift:
        trust_drop = expected_trust - observed_trust

        if trust_drop > 0.2:
            sev = DriftSeverity.HIGH
            summary = f"Significant trust degradation: trust dropped by {trust_drop:.2f} (expected: {expected_trust}, observed: {observed_trust})"
        elif trust_drop > 0.05:
            sev = DriftSeverity.MEDIUM
            summary = f"Moderate trust degradation: trust dropped by {trust_drop:.2f}"
        else:
            sev = DriftSeverity.LOW
            summary = "Trust levels stable"

        return AssuranceDrift(
            tenant_id=tenant_id,
            drift_type=DriftType.TRUST,
            severity=sev,
            expected_state={"expected_trust": expected_trust},
            observed_state={"observed_trust": observed_trust},
            difference_summary=summary,
            confidence=0.95,
            status=DriftStatus.DETECTED,
        )
