"""Runtime governance engine for Runtime Intelligence (Phase 5.57)."""

import logging
import uuid
from typing import Dict, Any, Optional
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
    "RESTART_SERVICE",
    "FAILOVER",
}


class RuntimeGovernanceEngine:
    """Evaluates governance requirements for runtime operations."""

    def evaluate_governance(
        self,
        tenant_id: str,
        action_name: str,
        parameters: Optional[Dict[str, Any]] = None,
        risk_level: Any = "MEDIUM",
    ) -> Dict[str, Any]:
        act_upper = action_name.strip().upper()
        risk_str = str(risk_level.value if hasattr(risk_level, "value") else risk_level).upper()

        is_high_risk_action = act_upper in HIGH_RISK_RUNTIME_ACTIONS
        is_high_risk_level = risk_str in ["HIGH", "CRITICAL"]

        if is_high_risk_action or is_high_risk_level:
            outcome = RuntimeGovernanceOutcome.REQUIRE_APPROVAL
            decision = "REQUIRE_APPROVAL"
            req_review = True
            reasoning = f"Action '{action_name}' classified as high risk (action_flag={is_high_risk_action}, risk_level={risk_str})"
        elif "ADVISORY" in act_upper:
            outcome = RuntimeGovernanceOutcome.ADVISORY_ONLY
            decision = "ADVISORY_ONLY"
            req_review = False
            reasoning = f"Action '{action_name}' is advisory only"
        else:
            outcome = RuntimeGovernanceOutcome.ALLOW
            decision = "ALLOW"
            req_review = False
            reasoning = f"Action '{action_name}' evaluated against risk level '{risk_str}' — allowed within normal boundaries"

        evaluation_id = f"gov_{uuid.uuid4().hex[:12]}"
        logger.info(f"Evaluated Runtime Governance for action '{action_name}' (tenant: '{tenant_id}') -> Decision: {decision}")
        return {
            "evaluation_id": evaluation_id,
            "tenant_id": tenant_id,
            "action_name": action_name,
            "action": action_name,
            "decision": decision,
            "outcome": outcome.value,
            "requires_human_approval": req_review,
            "requires_human_review": req_review,
            "reasoning": reasoning,
        }

    def enforce_approval_check(self, tenant_id: str, action_name: str, is_approved: bool) -> None:
        act_upper = action_name.strip().upper()
        if act_upper in HIGH_RISK_RUNTIME_ACTIONS and not is_approved:
            logger.warning(f"Blocked unapproved high-risk runtime action '{action_name}' for tenant '{tenant_id}'")
            raise HighRiskRuntimeActionRequiresApprovalException(action_name=action_name)
