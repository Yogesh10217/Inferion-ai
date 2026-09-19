"""Capacity governance engine for Capacity Intelligence (Phase 5.56)."""

import logging
from typing import Any, Dict

from app.capacity_intelligence.exceptions import HighRiskCapacityActionRequiresApprovalException
from app.capacity_intelligence.models import CapacityGovernanceOutcome

logger = logging.getLogger(__name__)

HIGH_RISK_CAPACITY_ACTIONS = {
    "PRODUCTION_SCALING_CHANGE",
    "LARGE_INFRASTRUCTURE_EXPANSION",
    "DATABASE_CAPACITY_MODIFICATION",
    "REGION_CAPACITY_CHANGE",
    "WORKLOAD_MIGRATION",
    "AGGRESSIVE_RESOURCE_REDUCTION",
    "PRODUCTION_RESOURCE_TERMINATION",
    "SCALING_POLICY_CHANGE",
}


class CapacityGovernanceEngine:
    """Evaluates policy, risk, cost, reliability, and reversibility outcomes for capacity operations."""

    def evaluate_governance(
        self, tenant_id: str, action_name: str, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        act_upper = action_name.upper()
        if act_upper in HIGH_RISK_CAPACITY_ACTIONS:
            outcome = CapacityGovernanceOutcome.REQUIRE_APPROVAL
        else:
            outcome = CapacityGovernanceOutcome.ALLOW

        logger.info(
            f"Evaluated Capacity Governance for action '{action_name}' (tenant: '{tenant_id}') -> Outcome: {outcome.value}"
        )
        return {
            "tenant_id": tenant_id,
            "action_name": action_name,
            "outcome": outcome.value,
            "requires_human_review": outcome == CapacityGovernanceOutcome.REQUIRE_APPROVAL,
        }

    def enforce_approval_check(self, tenant_id: str, action_name: str, is_approved: bool) -> None:
        act_upper = action_name.upper()
        if act_upper in HIGH_RISK_CAPACITY_ACTIONS and not is_approved:
            logger.warning(f"Blocked unapproved high-risk capacity action '{action_name}' for tenant '{tenant_id}'")
            raise HighRiskCapacityActionRequiresApprovalException(action_name=action_name)
