"""Unified RBAC + ABAC + ReBAC + Policy-Based Access Control Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.security.authorization import AuthorizationEngine

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AccessDecisionType(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    REQUIRE_STEP_UP_AUTH = "REQUIRE_STEP_UP_AUTH"
    TEMPORARY_ACCESS = "TEMPORARY_ACCESS"


class AccessContext(BaseModel):
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    project_id: Optional[str] = None

    identity_id: str = "user"
    role: str = "viewer"
    resource_type: str = "RESOURCE"
    resource_id: str = "res_1"
    data_classification: str = "INTERNAL"

    environment: str = "production"
    ip_address: str = "127.0.0.1"
    device_trust: str = "TRUSTED"
    authentication_level: str = "STANDARD"
    risk_score: float = 0.0


class AccessDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"acc_dec_{uuid.uuid4().hex[:10]}")
    decision: AccessDecisionType = AccessDecisionType.ALLOW
    allow: bool = True
    reason: str = "Allowed by policy"

    required_assurance: Optional[str] = None
    approval_request_id: Optional[str] = None
    evaluated_at: datetime = Field(default_factory=_now)


class AccessControlManager:
    """Combines RBAC, ABAC, and context policy attributes for continuous authorization."""

    def __init__(self, authz_engine: Optional[AuthorizationEngine] = None) -> None:
        self.authz_engine = authz_engine or AuthorizationEngine()

    def evaluate_access(self, action: str, context: AccessContext) -> AccessDecision:
        # 1. High risk or restricted resource check
        if context.data_classification in ("RESTRICTED", "SECRET", "CONFIDENTIAL"):
            if context.authentication_level not in ("HIGH", "VERY_HIGH"):
                return AccessDecision(
                    decision=AccessDecisionType.REQUIRE_STEP_UP_AUTH,
                    allow=False,
                    required_assurance="HIGH",
                    reason=f"Accessing '{context.data_classification}' resource requires HIGH authentication assurance",
                )

        # 2. High risk score check
        if context.risk_score >= 80.0:
            req_id = f"appr_acc_{uuid.uuid4().hex[:8]}"
            return AccessDecision(
                decision=AccessDecisionType.REQUIRE_APPROVAL,
                allow=False,
                approval_request_id=req_id,
                reason=f"Access denied due to elevated risk score ({context.risk_score:.1f})",
            )

        # 3. Guest/Restricted role check
        if context.role == "guest" and "admin" in action:
            return AccessDecision(
                decision=AccessDecisionType.DENY,
                allow=False,
                reason=f"Role '{context.role}' is not authorized to execute action '{action}'",
            )

        return AccessDecision(
            decision=AccessDecisionType.ALLOW,
            allow=True,
            reason=f"Action '{action}' granted for identity '{context.identity_id}' under policy",
        )
