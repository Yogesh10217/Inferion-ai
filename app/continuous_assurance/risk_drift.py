"""Risk drift analyzer for Continuous Assurance (Phase 5.54)."""

import logging
from typing import Dict, Any
from app.continuous_assurance.models import AssuranceDrift, DriftType, DriftSeverity, DriftStatus

logger = logging.getLogger(__name__)


class RiskDriftAnalyzer:
    """Analyzes risk score increases, volatility, and threshold violations."""

    def analyze_risk_drift(
        self, tenant_id: str, baseline_risk: float, current_risk: float
    ) -> AssuranceDrift:
        risk_diff = current_risk - baseline_risk

        if risk_diff > 0.3:
            sev = DriftSeverity.CRITICAL
            summary = f"Critical risk drift: risk increased by {risk_diff:.2f} (baseline: {baseline_risk}, current: {current_risk})"
        elif risk_diff > 0.1:
            sev = DriftSeverity.HIGH
            summary = f"Elevated risk drift: risk increased by {risk_diff:.2f} (baseline: {baseline_risk}, current: {current_risk})"
        elif risk_diff > 0.05:
            sev = DriftSeverity.MEDIUM
            summary = f"Minor risk drift: risk increased by {risk_diff:.2f}"
        else:
            sev = DriftSeverity.LOW
            summary = "Risk levels stable within normal parameters"

        return AssuranceDrift(
            tenant_id=tenant_id,
            drift_type=DriftType.RISK,
            severity=sev,
            expected_state={"baseline_risk": baseline_risk},
            observed_state={"current_risk": current_risk},
            difference_summary=summary,
            confidence=0.94,
            status=DriftStatus.DETECTED,
        )
