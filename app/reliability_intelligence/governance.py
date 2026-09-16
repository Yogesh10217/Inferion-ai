"""Reliability governance engine (Phase 5.55)."""

import logging
from typing import Any, Dict

from app.reliability_intelligence.exceptions import HighRiskReliabilityActionRequiresApprovalException
from app.reliability_intelligence.models import GovernanceOutcome

logger = logging.getLogger(__name__)


class ReliabilityGovernanceEngine:
    """Evaluates governance policy boundary rules for reliability actions."""

    HIGH_RISK_ACTIONS = {
        "production_failover",
        "region_shutdown",
        "database_recovery",
        "traffic_migration",
        "chaos_experiment",
        "forced_degraded_mode",
        "large_scale_rollback",
    }

    def evaluate_governance(
        self, tenant_id: str, action_type: str, risk_level: str = "MEDIUM"
    ) -> Dict[str, Any]:
        action_clean = action_type.lower().strip()
        is_high_risk = action_clean in self.HIGH_RISK_ACTIONS or risk_level.upper() == "HIGH"

        if is_high_risk:
            outcome = GovernanceOutcome.REQUIRE_APPROVAL
            rationale = f"Reliability action '{action_type}' is high-risk and requires human approval."
        else:
            outcome = GovernanceOutcome.ALLOW
            rationale = f"Reliability action '{action_type}' within approved low/medium risk boundaries."

        logger.info(f"Evaluated governance for action '{action_type}' (tenant: '{tenant_id}') -> Outcome: {outcome.value}")

        return {
            "outcome": outcome.value,
            "action_type": action_type,
            "risk_level": risk_level,
            "requires_approval": is_high_risk,
            "rationale": rationale,
        }

    def enforce_approval_check(self, tenant_id: str, action_type: str, is_approved: bool = False) -> None:
        res = self.evaluate_governance(tenant_id, action_type, risk_level="HIGH")
        if res["requires_approval"] and not is_approved:
            logger.warning(f"Unapproved high-risk reliability action blocked: {action_type}")
            raise HighRiskReliabilityActionRequiresApprovalException(action_id=action_type)
