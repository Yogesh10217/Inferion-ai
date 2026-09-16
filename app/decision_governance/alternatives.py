"""Alternative decision analysis and comparative tradeoff evaluation."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AlternativeType(str, Enum):
    STATUS_QUO = "STATUS_QUO"
    MINIMAL_CHANGE = "MINIMAL_CHANGE"
    COMPREHENSIVE = "COMPREHENSIVE"
    AGGRESSIVE = "AGGRESSIVE"
    CONSERVATIVE = "CONSERVATIVE"
    CUSTOM = "CUSTOM"


class AlternativeTradeoff(BaseModel):
    category: str
    gain: str
    sacrifice: str
    score_delta: float = 0.0


class AlternativeScore(BaseModel):
    overall_score: float = 0.0
    cost_score: float = 0.0
    risk_score: float = 0.0
    reliability_score: float = 0.0
    compliance_score: float = 0.0
    speed_score: float = 0.0


class DecisionAlternative(BaseModel):
    alternative_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    tenant_id: str
    name: str
    description: str
    alternative_type: AlternativeType = AlternativeType.MINIMAL_CHANGE
    scores: AlternativeScore = Field(default_factory=AlternativeScore)
    tradeoffs: List[AlternativeTradeoff] = Field(default_factory=list)
    risks: List[str] = Field(default_factory=list)
    benefits: List[str] = Field(default_factory=list)
    estimated_cost_usd: float = 0.0
    is_recommended: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AlternativeAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    tenant_id: str
    alternatives: List[DecisionAlternative] = Field(default_factory=list)
    best_alternative_id: Optional[str] = None
    comparison_summary: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionAlternativeManager:
    """Manages comparison and ranking of decision alternatives."""

    def __init__(self) -> None:
        self._alternatives: Dict[str, DecisionAlternative] = {}

    def create_alternative(
        self,
        tenant_id: str,
        decision_id: str,
        name: str,
        description: str,
        alternative_type: AlternativeType = AlternativeType.MINIMAL_CHANGE,
        scores: Optional[AlternativeScore] = None,
        tradeoffs: Optional[List[AlternativeTradeoff]] = None,
        risks: Optional[List[str]] = None,
        benefits: Optional[List[str]] = None,
        estimated_cost_usd: float = 0.0,
        is_recommended: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DecisionAlternative:
        alt = DecisionAlternative(
            tenant_id=tenant_id,
            decision_id=decision_id,
            name=name,
            description=description,
            alternative_type=alternative_type,
            scores=scores or AlternativeScore(),
            tradeoffs=tradeoffs or [],
            risks=risks or [],
            benefits=benefits or [],
            estimated_cost_usd=estimated_cost_usd,
            is_recommended=is_recommended,
            metadata=metadata or {},
        )
        self._alternatives[alt.alternative_id] = alt
        return alt

    def list_alternatives_for_decision(self, decision_id: str, tenant_id: str) -> List[DecisionAlternative]:
        alts = [a for a in self._alternatives.values() if a.decision_id == decision_id and a.tenant_id == tenant_id]
        return sorted(alts, key=lambda x: x.scores.overall_score, reverse=True)

    def evaluate_alternatives(self, decision_id: str, tenant_id: str) -> AlternativeAssessment:
        alts = self.list_alternatives_for_decision(decision_id, tenant_id)
        best_id = alts[0].alternative_id if alts else None
        summary = f"Evaluated {len(alts)} alternatives. Top choice: {alts[0].name if alts else 'None'}."
        return AlternativeAssessment(
            decision_id=decision_id,
            tenant_id=tenant_id,
            alternatives=alts,
            best_alternative_id=best_id,
            comparison_summary=summary,
        )
