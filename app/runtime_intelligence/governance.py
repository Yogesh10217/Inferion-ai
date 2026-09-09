"""Runtime governance engine for Runtime Intelligence (Phase 5.54)."""

import logging
from typing import Dict, Any
from app.runtime_intelligence.models import RuntimeGovernanceOutcome
from app.runtime_intelligence.exceptions import HighRiskRuntimeActionRequiresApprovalException

logger = logging.getLogger(__name__)

HIGH_RISK_RUNTIME_ACTIONS = {
    "PRODUCTION_RECOVERY",
    "PRODUCTION_ROLLBACK",
    "SERVICE_SHUTDOWN",
    "CREDENTIAL_REVOCATION",
    "LARGE_INFRASTRUCTURE_SCALING",
    "CROSS_REGION_FAILOVER",
    "DATA_RECOVERY",
    "SECURITY_CONTAINMENT",
}


class RuntimeGovernanceEngine:
    """Evaluates governance requirements for runtime operations."""

    def evaluate_governance(
        self, tenant_id: str, action_name: str, parameters: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        act_upper = action_name.upper()
        if act_upper in HIGH_RISK_RUNTIME_ACTIONS:
            outcome = RuntimeGovernanceOutcome.REQUIRE_APPROVAL
        else:
            outcome = RuntimeGovernanceOutcome.ALLOW

        logger.info(f"Evaluated Runtime Governance for action '{action_name}' (tenant: '{tenant_id}') -> Outcome: {outcome.value}")
        return {
            "tenant_id": tenant_id,
            "action_name": action_name,
            "outcome": outcome.value,
            "requires_human_review": outcome == RuntimeGovernanceOutcome.REQUIRE_APPROVAL,
        }

    def enforce_approval_check(self, tenant_id: str, action_name: str, is_approved: bool) -> None:
        act_upper = action_name.upper()
        if act_upper in HIGH_RISK_RUNTIME_ACTIONS and not is_approved:
            logger.warning(f"Blocked unapproved high-risk runtime action '{action_name}' for tenant '{tenant_id}'")
            raise HighRiskRuntimeActionRequiresApprovalException(action_name=action_name)
