"""Governed Authorization Intelligence (Phase 5.39)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import CrossTenantAccessIntelligenceException, AccessPolicyViolationException


class AuthorizationDecisionOutcome(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class AuthorizationConstraint(BaseModel):
    """Constraint applied to authorization decision."""
    constraint_id: str = Field(default_factory=lambda: f"cnst_{uuid.uuid4().hex[:8]}")
    name: str
    constraint_type: str  # IP_RESTRICTION, TIME_WINDOW, MFA_REQUIRED, RATE_LIMIT, RESOURCE_BOUND
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AuthorizationEvidence(BaseModel):
    """Evidence evaluating authorization request."""
    evidence_id: str = Field(default_factory=lambda: f"evid_{uuid.uuid4().hex[:8]}")
    evaluator: str = "UnifiedPolicyEvaluator"
    policy_code: Optional[str] = None
    risk_score: float = 0.0
    passed: bool = True
    details: Dict[str, Any] = Field(default_factory=dict)


class AuthorizationRequest(BaseModel):
    """Governed Authorization Request."""
    request_id: str = Field(default_factory=lambda: f"auth_req_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    subject_identity_id: str
    action: str
    resource_id: str
    resource_type: str
    context: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuthorizationDecision(BaseModel):
    """Governed Authorization Decision."""
    decision_id: str = Field(default_factory=lambda: f"auth_dec_{uuid.uuid4().hex[:12]}")
    request_id: str
    tenant_id: str
    outcome: AuthorizationDecisionOutcome
    reason: str
    risk_score: float = 0.0
    constraints: List[AuthorizationConstraint] = Field(default_factory=list)
    evidence: List[AuthorizationEvidence] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuthorizationManager:
    """Governed Authorization Intelligence Manager."""

    def __init__(self) -> None:
        self._requests: Dict[str, AuthorizationRequest] = {}
        self._decisions: Dict[str, AuthorizationDecision] = {}

    def evaluate_authorization(
        self,
        tenant_id: str,
        subject_identity_id: str,
        action: str,
        resource_id: str,
        resource_type: str,
        context: Optional[Dict[str, Any]] = None,
        override_outcome: Optional[AuthorizationDecisionOutcome] = None,
    ) -> AuthorizationDecision:
        context = context or {}
        req = AuthorizationRequest(
            tenant_id=tenant_id,
            subject_identity_id=subject_identity_id,
            action=action,
            resource_id=resource_id,
            resource_type=resource_type,
            context=context,
        )
        self._requests[req.request_id] = req

        is_high_risk = context.get("is_high_risk", False) or action.upper() in ["DELETE", "GRANT_ADMIN", "DISABLE_AUDIT"]
        
        if override_outcome:
            outcome = override_outcome
            reason = f"Explicit authorization outcome {override_outcome.value} requested."
        elif context.get("is_blocked", False):
            outcome = AuthorizationDecisionOutcome.BLOCK
            reason = "Action blocked by active governance policy."
        elif context.get("is_denied", False):
            outcome = AuthorizationDecisionOutcome.DENY
            reason = "Action denied due to missing entitlement."
        elif context.get("is_restricted", False):
            outcome = AuthorizationDecisionOutcome.RESTRICT
            reason = "Action permitted under restricted scope constraints."
        elif is_high_risk or context.get("requires_approval", False):
            outcome = AuthorizationDecisionOutcome.REQUIRE_APPROVAL
            reason = "High-risk action on resource requires human approval."
        else:
            outcome = AuthorizationDecisionOutcome.ALLOW
            reason = "Authorization request satisfied policy requirements."

        evid = AuthorizationEvidence(
            policy_code="POL_ACCESS_01",
            risk_score=85.0 if is_high_risk else 15.0,
            passed=outcome in [AuthorizationDecisionOutcome.ALLOW, AuthorizationDecisionOutcome.RESTRICT, AuthorizationDecisionOutcome.REQUIRE_APPROVAL],
            details={"action": action, "resource_id": resource_id},
        )

        dec = AuthorizationDecision(
            request_id=req.request_id,
            tenant_id=tenant_id,
            outcome=outcome,
            reason=reason,
            risk_score=evid.risk_score,
            evidence=[evid],
        )
        self._decisions[dec.decision_id] = dec
        return dec

    def get_decision(self, tenant_id: str, decision_id: str) -> AuthorizationDecision:
        dec = self._decisions.get(decision_id)
        if not dec or dec.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return dec
