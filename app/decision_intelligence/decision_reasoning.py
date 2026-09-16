"""
Explainable Decision Reasoning Subsystem.
Generates human-readable, transparent, and auditable reasoning chains for decision recommendations.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class DecisionReasoningChain(BaseModel):
    reasoning_id: str = Field(default_factory=lambda: f"reason_{uuid.uuid4().hex[:12]}")
    decision_id: str
    tenant_id: str
    version: str = "1.0.0"
    premises: List[str] = Field(default_factory=list)
    policy_evaluations_summary: List[str] = Field(default_factory=list)
    risk_tradeoffs_summary: List[str] = Field(default_factory=list)
    conclusion: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionReasoningEngine:
    """Generates explainable decision reasoning documentation."""

    def __init__(self) -> None:
        self._chains: Dict[str, DecisionReasoningChain] = {}

    def generate_reasoning_chain(
        self,
        decision_id: str,
        tenant_id: str,
        premises: List[str],
        policy_summary: List[str],
        tradeoff_summary: List[str],
        conclusion: str,
    ) -> DecisionReasoningChain:
        chain = DecisionReasoningChain(
            decision_id=decision_id,
            tenant_id=tenant_id,
            premises=premises,
            policy_evaluations_summary=policy_summary,
            risk_tradeoffs_summary=tradeoff_summary,
            conclusion=conclusion,
        )
        self._chains[decision_id] = chain
        return chain

    def get_reasoning_chain(self, decision_id: str) -> Optional[DecisionReasoningChain]:
        return self._chains.get(decision_id)
