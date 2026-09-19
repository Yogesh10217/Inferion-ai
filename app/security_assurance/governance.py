"""Security Governance Engine & Policy Gatekeeper."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from app.security_assurance.exceptions import HighRiskSecurityActionRequiresApprovalException

logger = logging.getLogger(__name__)


class SecurityGovernanceRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"gov-req-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    action: str
    target_resource_id: str
    is_high_risk: bool = False
    approved_by: Optional[str] = None
    approval_status: str = "PENDING"  # PENDING, APPROVED, REJECTED


class SecurityGovernanceResult(BaseModel):
    request_id: str
    tenant_id: str
    decision: str  # ALLOWED, REQUIRE_APPROVAL, DENIED
    reason: str
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityGovernanceEngine:
    """Evaluates security actions against enterprise governance policies and enforces human approvals."""

    def evaluate_security_action(
        self,
        tenant_id: str,
        action: str,
        target_resource_id: str,
        is_high_risk: bool = False,
        approved_by: Optional[str] = None,
    ) -> SecurityGovernanceResult:
        if is_high_risk and not approved_by:
            logger.warning(
                f"[SECURITY GOVERNANCE] High-risk action '{action}' on '{target_resource_id}' requires human approval."
            )
            return SecurityGovernanceResult(
                request_id=f"gov-req-{uuid.uuid4().hex[:8]}",
                tenant_id=tenant_id,
                decision="REQUIRE_APPROVAL",
                reason="High-risk security action requires human approval before delegation/execution.",
            )

        return SecurityGovernanceResult(
            request_id=f"gov-req-{uuid.uuid4().hex[:8]}",
            tenant_id=tenant_id,
            decision="ALLOWED",
            reason="Action conforms to security governance policies.",
        )

    def enforce_execution(
        self,
        tenant_id: str,
        action: str,
        target_resource_id: str,
        is_high_risk: bool = False,
        approved_by: Optional[str] = None,
    ) -> bool:
        eval_result = self.evaluate_security_action(
            tenant_id=tenant_id,
            action=action,
            target_resource_id=target_resource_id,
            is_high_risk=is_high_risk,
            approved_by=approved_by,
        )
        if eval_result.decision == "REQUIRE_APPROVAL":
            raise HighRiskSecurityActionRequiresApprovalException(
                f"Action '{action}' on target '{target_resource_id}' requires explicit human approval."
            )
        return True
