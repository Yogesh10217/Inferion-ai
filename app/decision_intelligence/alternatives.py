"""Alternative Decision Modeling Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.decision_intelligence.exceptions import DecisionIntelligenceException, CrossTenantDecisionAccessException


class AlternativeStatus(str, Enum):
    PROPOSED = "PROPOSED"
    EVALUATED = "EVALUATED"
    RECOMMENDED = "RECOMMENDED"
    REJECTED = "REJECTED"


class AlternativeScore(BaseModel):
    cost_score: float = 80.0
    benefit_score: float = 85.0
    risk_score: float = 20.0
    trust_score: float = 90.0
    compliance_score: float = 90.0
    resilience_score: float = 85.0
    complexity_score: float = 30.0
    alignment_score: float = 90.0
    total_score: float = 82.5


class DecisionAlternative(BaseModel):
    alternative_id: str = Field(default_factory=lambda: f"alt_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    context_id: str
    title: str
    description: str
    score: AlternativeScore = Field(default_factory=AlternativeScore)
    status: AlternativeStatus = AlternativeStatus.PROPOSED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AlternativeManager:
    """Manages creation, scoring, and evaluation of decision alternatives."""

    def __init__(self) -> None:
        self._alternatives: Dict[str, List[DecisionAlternative]] = {}

    def create_alternative(
        self,
        tenant_id: str,
        context_id: str,
        title: str,
        description: str,
        score: Optional[AlternativeScore] = None,
    ) -> DecisionAlternative:
        alt = DecisionAlternative(
            tenant_id=tenant_id,
            context_id=context_id,
            title=title,
            description=description,
            score=score or AlternativeScore(),
        )
        if tenant_id not in self._alternatives:
            self._alternatives[tenant_id] = []
        self._alternatives[tenant_id].append(alt)
        return alt

    def list_alternatives(self, tenant_id: str, context_id: str) -> List[DecisionAlternative]:
        alts = self._alternatives.get(tenant_id, [])
        return [a for a in alts if a.context_id == context_id]
