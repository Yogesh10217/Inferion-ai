"""Policy drift analyzer for Continuous Assurance (Phase 5.54)."""

import logging
from typing import Dict, Any
from app.continuous_assurance.models import AssuranceDrift, DriftType, DriftSeverity, DriftStatus

logger = logging.getLogger(__name__)


class PolicyDriftAnalyzer:
    """Analyzes differences between approved policy posture and runtime policy behavior."""

    def analyze_policy_drift(
        self, tenant_id: str, expected_policy: Dict[str, Any], runtime_policy: Dict[str, Any]
    ) -> AssuranceDrift:
        violations = []
        for rule, exp_val in expected_policy.items():
            run_val = runtime_policy.get(rule)
            if run_val != exp_val:
                violations.append(f"Rule '{rule}': expected '{exp_val}', runtime '{run_val}'")

        if violations:
            summary = "Policy drift detected: " + "; ".join(violations)
            sev = DriftSeverity.HIGH if len(violations) > 1 else DriftSeverity.MEDIUM
        else:
            summary = "No policy drift detected"
            sev = DriftSeverity.LOW

        return AssuranceDrift(
            tenant_id=tenant_id,
            drift_type=DriftType.POLICY,
            severity=sev,
            expected_state=expected_policy,
            observed_state=runtime_policy,
            difference_summary=summary,
            confidence=0.97,
            status=DriftStatus.DETECTED,
        )
