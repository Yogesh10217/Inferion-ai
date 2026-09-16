"""Continuous assurance governance engine (Phase 5.54)."""

import logging
from typing import Any, Dict

from app.continuous_assurance.exceptions import HighRiskContinuousAssuranceActionRequiresApprovalException
from app.continuous_assurance.models import GovernanceDecisionOutcome

logger = logging.getLogger(__name__)


class ContinuousAssuranceGovernanceEngine:
    """Evaluates continuous governance boundary rules (ALLOW, DENY, REQUIRE_APPROVAL, ADVISORY_ONLY)."""

    def evaluate_governance(
        self, tenant_id: str, action_type: str, risk_level: str = "MEDIUM"
    ) -> Dict[str, Any]:
        high_risk_actions = {
            "disable_identity",
            "rotate_credential",
            "rollback_deployment",
            "modify_policy",
            "change_infrastructure",
            "block_network_access",
            "restart_service",
            "modify_database",
        }

        action_clean = action_type.lower().strip()
        is_high_risk = action_clean in high_risk_actions or risk_level.upper() == "HIGH"

        if is_high_risk:
            outcome = GovernanceDecisionOutcome.REQUIRE_APPROVAL
            rationale = f"Action '{action_type}' is high-risk and requires human approval."
        else:
            outcome = GovernanceDecisionOutcome.ALLOW
            rationale = f"Action '{action_type}' within low/medium risk policy boundaries."

        logger.info(f"Evaluated governance for tenant '{tenant_id}', action '{action_type}' -> Outcome: {outcome.value}")

        return {
            "outcome": outcome.value,
            "action_type": action_type,
            "risk_level": risk_level,
            "requires_approval": is_high_risk,
            "rationale": rationale,
        }

    def enforce_approval_check(self, tenant_id: str, action_type: str, is_approved: bool = False) -> None:
        eval_res = self.evaluate_governance(tenant_id, action_type, risk_level="HIGH")
        if eval_res["requires_approval"] and not is_approved:
            logger.warning(f"Unapproved high-risk continuous assurance action blocked: {action_type}")
            raise HighRiskContinuousAssuranceActionRequiresApprovalException(action_id=action_type)
