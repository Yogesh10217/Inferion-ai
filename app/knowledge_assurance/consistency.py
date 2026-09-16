"""Knowledge consistency assessment across cross-platform domains."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ConsistencyDimension(str, Enum):
    SOURCES = "SOURCES"
    POLICIES = "POLICIES"
    DECISIONS = "DECISION"
    PROCEDURES = "PROCEDURES"
    INCIDENTS = "INCIDENTS"
    MODELS = "MODELS"
    DATASETS = "DATASETS"


class ConsistencyFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dimension: ConsistencyDimension
    description: str
    severity: str = "LOW"


class ConsistencyScore(BaseModel):
    overall_consistency_score: float = 0.92
    dimension_scores: Dict[str, float] = Field(default_factory=dict)


class KnowledgeConsistencyAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    consistency_score: ConsistencyScore
    findings: List[ConsistencyFinding] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def overall_score(self) -> float:
        return self.consistency_score.overall_consistency_score


class KnowledgeConsistencyManager:
    """Evaluates cross-domain knowledge consistency."""

    def __init__(self) -> None:
        self._assessments: Dict[str, KnowledgeConsistencyAssessment] = {}

    def assess_consistency(
        self,
        tenant_id: str,
        target_resource_id: Optional[str] = None,
        reference_ids: Optional[List[str]] = None,
        findings: Optional[List[ConsistencyFinding]] = None,
    ) -> KnowledgeConsistencyAssessment:
        dim_scores = {d.value: 0.92 for d in ConsistencyDimension}
        if findings:
            for f in findings:
                if f.severity == "HIGH":
                    dim_scores[f.dimension.value] = min(dim_scores.get(f.dimension.value, 0.92), 0.60)

        overall = sum(dim_scores.values()) / len(dim_scores) if dim_scores else 0.92

        assessment = KnowledgeConsistencyAssessment(
            tenant_id=tenant_id,
            consistency_score=ConsistencyScore(overall_consistency_score=overall, dimension_scores=dim_scores),
            findings=findings or [],
        )
        self._assessments[assessment.assessment_id] = assessment
        return assessment
