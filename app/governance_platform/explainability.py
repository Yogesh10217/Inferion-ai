"""Deterministic Explainability Engine for Governance Decisions."""

from datetime import datetime, timezone
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.governance_platform.decision import GovernanceDecisionRecord
from app.governance_platform.policy_evaluation import GovernanceDecision

logger = logging.getLogger(__name__)


class DecisionExplanation(BaseModel):
    decision_id: str
    action: str
    target_resource_id: str
    outcome: str
    primary_reason: str
    matched_policies: List[str]
    violations: List[str]
    risk_score: float
    evidence_ids: List[str]
    approved_by: Optional[str] = None
    is_deterministic: bool = True
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExplainabilityEngine:
    """Generates deterministic, evidence-backed explanations from evaluation data without LLM hallucination."""

    def explain_decision(self, record: GovernanceDecisionRecord) -> DecisionExplanation:
        if record.decision == GovernanceDecision.ALLOW:
            outcome = "ALLOWED"
            primary_reason = f"Action '{record.action}' on resource '{record.target_resource_id}' complied with all evaluated governance policies."
        elif record.decision == GovernanceDecision.REQUIRE_APPROVAL:
            outcome = "APPROVAL_REQUIRED"
            primary_reason = f"Action '{record.action}' required explicit authorization due to elevated risk or policy constraints."
        else:
            outcome = f"BLOCKED ({record.decision.value})"
            primary_reason = f"Action '{record.action}' violated governance policies: {'; '.join(record.violations) if record.violations else 'Policy restriction'}"

        expl = DecisionExplanation(
            decision_id=record.decision_id,
            action=record.action,
            target_resource_id=record.target_resource_id,
            outcome=outcome,
            primary_reason=primary_reason,
            matched_policies=record.matched_policies,
            violations=record.violations,
            risk_score=record.risk_score,
            evidence_ids=record.evidence_ids,
            approved_by=record.approved_by,
        )
        logger.info(f"[EXPLAINABILITY] Generated explanation for decision '{record.decision_id}': Outcome = {outcome}")
        return expl
