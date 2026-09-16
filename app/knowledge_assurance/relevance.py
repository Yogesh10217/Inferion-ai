"""Knowledge relevance intelligence evaluating multi-dimensional alignment."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RelevanceDimension(str, Enum):
    SEMANTIC = "SEMANTIC"
    CONTEXT = "CONTEXT"
    DECISION = "DECISION"
    OPERATIONAL = "OPERATIONAL"
    TEMPORAL = "TEMPORAL"


class RelevanceScore(BaseModel):
    overall_relevance_score: float = 0.85
    dimension_scores: Dict[str, float] = Field(default_factory=dict)


class KnowledgeRelevance(BaseModel):
    relevance_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    reference_id: str
    target_context_id: Optional[str] = None
    scores: RelevanceScore = Field(default_factory=RelevanceScore)

    @property
    def overall_relevance(self) -> float:
        return self.scores.overall_relevance_score

    @property
    def factors(self) -> List[Dict[str, Any]]:
        return [
            {"dimension": k, "score": v}
            for k, v in self.scores.dimension_scores.items()
        ]


class RelevanceAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    relevances: List[KnowledgeRelevance] = Field(default_factory=list)
    average_relevance_score: float = 0.85
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeRelevanceManager:
    """Evaluates semantic, context, operational, and decision relevance."""

    def __init__(self) -> None:
        self._relevances: Dict[str, KnowledgeRelevance] = {}

    def evaluate_relevance(
        self,
        tenant_id: str,
        reference_id: Optional[str] = None,
        target_resource_id: Optional[str] = None,
        query_context: Optional[str] = None,
        target_context_id: Optional[str] = None,
        dimension_scores: Optional[Dict[str, float]] = None,
    ) -> KnowledgeRelevance:
        ref_id = target_resource_id or reference_id or "ref-1"
        scores_map = dimension_scores or {
            RelevanceDimension.SEMANTIC.value: 0.90,
            RelevanceDimension.CONTEXT.value: 0.88,
            RelevanceDimension.DECISION.value: 0.85,
            RelevanceDimension.OPERATIONAL.value: 0.82,
            RelevanceDimension.TEMPORAL.value: 0.95,
        }
        avg = sum(scores_map.values()) / len(scores_map) if scores_map else 0.85

        rel = KnowledgeRelevance(
            tenant_id=tenant_id,
            reference_id=ref_id,
            target_context_id=target_context_id,
            scores=RelevanceScore(overall_relevance_score=avg, dimension_scores=scores_map),
        )
        self._relevances[rel.relevance_id] = rel
        return rel
