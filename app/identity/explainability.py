"""Deterministic Authorization Decision Explainability Subsystem."""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.identity.access_control import AccessDecision, AccessContext

logger = logging.getLogger(__name__)


class AuthorizationExplanation(BaseModel):
    decision_id: str
    identity_id: str
    action: str
    resource_id: str
    outcome: str

    primary_reason: str
    contributing_factors: List[str] = Field(default_factory=list)
    required_assurance: Optional[str] = None
    approval_request_id: Optional[str] = None

    is_deterministic: bool = True
    explained_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExplainabilityEngine:
    """Generates deterministic, evidence-backed explanations for authorization decisions without LLM hallucination."""

    def explain_access_decision(self, action: str, context: AccessContext, decision: AccessDecision) -> AuthorizationExplanation:
        factors = [
            f"Identity Role: {context.role}",
            f"Data Classification: {context.data_classification}",
            f"Authentication Assurance Level: {context.authentication_level}",
            f"Risk Score: {context.risk_score:.1f}",
            f"Device Trust: {context.device_trust}",
        ]

        outcome = "ALLOWED" if decision.allow else f"DENIED ({decision.decision.value})"

        expl = AuthorizationExplanation(
            decision_id=decision.decision_id,
            identity_id=context.identity_id,
            action=action,
            resource_id=context.resource_id,
            outcome=outcome,
            primary_reason=decision.reason,
            contributing_factors=factors,
            required_assurance=decision.required_assurance,
            approval_request_id=decision.approval_request_id,
        )
        logger.info(f"[IDENTITY EXPLAINABILITY] Generated explanation for decision '{decision.decision_id}': Outcome = {outcome}")
        return expl
