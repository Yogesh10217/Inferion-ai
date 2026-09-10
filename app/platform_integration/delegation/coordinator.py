"""Cross-Phase Delegation Coordinator (Phase 5.58)."""

import logging
from typing import Dict, Any, List, Optional
import uuid

from app.platform_contracts.delegation import (
    DelegationRequest,
    DelegationTarget,
    DelegationStatus,
)
from app.platform_integration.models import (
    GovernanceDecision,
    CrossPhaseRecommendation,
    TraceContext,
    RiskLevel,
)
from app.platform_integration.exceptions import (
    HighRiskPlatformIntegrationActionRequiresApprovalException,
)
from app.platform_integration.governance.approvals import PlatformIntegrationApprovalManager

logger = logging.getLogger(__name__)


class CrossPhaseDelegationCoordinator:
    """Coordinates advisory delegations by producing standardized DelegationRequest objects."""

    def __init__(self, approval_manager: Optional[PlatformIntegrationApprovalManager] = None) -> None:
        self.approval_manager = approval_manager or PlatformIntegrationApprovalManager()

    def create_delegation(
        self,
        tenant_id: str,
        recommendation: CrossPhaseRecommendation,
        governance_decision: GovernanceDecision,
        approval_id: Optional[str] = None,
        approval_token: Optional[str] = None,
        trace_context: Optional[TraceContext] = None,
    ) -> DelegationRequest:
        # Enforce human approval guard for high/critical risk actions
        if governance_decision == GovernanceDecision.REQUIRE_APPROVAL:
            if not approval_id or not approval_token:
                raise HighRiskPlatformIntegrationActionRequiresApprovalException(
                    f"High-risk action '{recommendation.action}' requires approved human approval token."
                )
            if not self.approval_manager.validate_token(approval_id, approval_token):
                raise HighRiskPlatformIntegrationActionRequiresApprovalException(
                    f"Invalid or expired approval token for action '{recommendation.action}'."
                )

        ctx = trace_context or recommendation.trace_context or TraceContext(tenant_id=tenant_id)
        target = DelegationTarget.PLATFORM_OPERATIONS

        del_id = f"delreq_{uuid.uuid4().hex[:12]}"
        payload = {
            "action": recommendation.action,
            "target_platform": recommendation.target_platform.value,
            "description": recommendation.description,
            "parameters": recommendation.parameters,
            "trace_id": ctx.trace_id,
            "correlation_id": ctx.correlation_id,
            "recommendation_id": recommendation.recommendation_id,
            "governance_decision": governance_decision.value,
            "approval_id": approval_id,
        }

        req = DelegationRequest(
            delegation_id=del_id,
            tenant_id=tenant_id,
            target=target,
            action=recommendation.action,
            status=DelegationStatus.CREATED,
            payload=payload,
        )

        logger.info(f"Emitted standardized DelegationRequest {req.delegation_id} for action '{req.action}'")
        return req
