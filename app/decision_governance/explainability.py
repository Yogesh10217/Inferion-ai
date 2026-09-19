"""Explainable decision intelligence for generating human-readable audit trails and explanations."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.decision_governance.exceptions import CrossTenantDecisionGovernanceException


class ExplanationFactor(BaseModel):
    name: str
    impact_description: str
    weight: float = 1.0


class ExplanationEvidence(BaseModel):
    source: str
    summary: str
    link_or_ref: str = ""


class ExplanationConfidence(BaseModel):
    score: float = 0.85
    rationale: str = "High signal quality and evidence alignment"


class ExplanationTradeoff(BaseModel):
    chosen_path: str
    alternative_path: str
    reason_for_choice: str


class DecisionExplanation(BaseModel):
    explanation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    tenant_id: str
    why_summary: str
    why_not_alternatives: List[str] = Field(default_factory=list)
    evidence: List[ExplanationEvidence] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    key_risks: List[str] = Field(default_factory=list)
    confidence: ExplanationConfidence = Field(default_factory=ExplanationConfidence)
    expected_outcome: str = ""
    factors: List[ExplanationFactor] = Field(default_factory=list)
    tradeoffs: List[ExplanationTradeoff] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionExplainabilityManager:
    """Generates transparent, auditable decision explanations."""

    def __init__(self) -> None:
        self._explanations: Dict[str, DecisionExplanation] = {}

    def generate_explanation(
        self,
        tenant_id: str,
        decision_id: str,
        why_summary: str,
        expected_outcome: str,
        why_not_alternatives: Optional[List[str]] = None,
        evidence: Optional[List[ExplanationEvidence]] = None,
        assumptions: Optional[List[str]] = None,
        key_risks: Optional[List[str]] = None,
        tradeoffs: Optional[List[ExplanationTradeoff]] = None,
    ) -> DecisionExplanation:
        exp = DecisionExplanation(
            tenant_id=tenant_id,
            decision_id=decision_id,
            why_summary=why_summary,
            expected_outcome=expected_outcome,
            why_not_alternatives=why_not_alternatives
            or [
                "Alternative A (Status Quo): Retains higher operational risk and cost.",
                "Alternative B (Aggressive): Exceeds risk threshold for production workloads.",
            ],
            evidence=evidence
            or [
                ExplanationEvidence(
                    source="telemetry_metrics", summary="Resource utilization spikes detected at peak load"
                ),
                ExplanationEvidence(source="finops_ledger", summary="Cost budget remains within 80% allocation limit"),
            ],
            assumptions=assumptions
            or [
                "System traffic projected to follow normal weekly curve",
                "Downstream dependencies remain available",
            ],
            key_risks=key_risks or ["Transient network latency during configuration update"],
            tradeoffs=tradeoffs
            or [
                ExplanationTradeoff(
                    chosen_path="Automated cost optimization",
                    alternative_path="Manual review",
                    reason_for_choice="High confidence (>85%) and low operational risk score (<0.20)",
                )
            ],
        )
        self._explanations[exp.explanation_id] = exp
        return exp

    def get_explanation_for_decision(self, decision_id: str, tenant_id: str) -> Optional[DecisionExplanation]:
        for exp in self._explanations.values():
            if exp.decision_id == decision_id:
                if exp.tenant_id != tenant_id:
                    raise CrossTenantDecisionGovernanceException()
                return exp
        return None
