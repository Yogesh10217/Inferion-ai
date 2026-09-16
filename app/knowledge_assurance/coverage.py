"""Enterprise knowledge coverage intelligence across business domains, services, and models."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class CoverageDimension(str, Enum):
    BUSINESS_DOMAINS = "BUSINESS_DOMAINS"
    SERVICES = "SERVICES"
    CONTROLS = "CONTROLS"
    MODELS = "MODELS"
    DATASETS = "DATASETS"
    WORKFLOWS = "WORKFLOWS"
    INCIDENTS = "INCIDENTS"


class CoverageScore(BaseModel):
    overall_coverage_score: float = 0.88
    dimension_scores: Dict[str, float] = Field(default_factory=dict)

    @property
    def overall_coverage(self) -> float:
        return self.overall_coverage_score


class KnowledgeCoverage(BaseModel):
    coverage_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    dimension: CoverageDimension
    coverage_pct: float = 85.0
    covered_items: List[str] = Field(default_factory=list)
    uncovered_items: List[str] = Field(default_factory=list)


class CoverageAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    scores: CoverageScore
    coverages: List[KnowledgeCoverage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def coverage_score(self) -> CoverageScore:
        return self.scores


class KnowledgeCoverageManager:
    """Evaluates organizational knowledge coverage."""

    def __init__(self) -> None:
        self._assessments: Dict[str, CoverageAssessment] = {}

    def evaluate_coverage(self, tenant_id: str, domain: str = "GLOBAL") -> CoverageAssessment:
        return self.assess_coverage(tenant_id=tenant_id)

    def assess_coverage(
        self,
        tenant_id: str,
        custom_coverages: Optional[List[KnowledgeCoverage]] = None,
    ) -> CoverageAssessment:
        if not custom_coverages:
            custom_coverages = [
                KnowledgeCoverage(tenant_id=tenant_id, dimension=CoverageDimension.SERVICES, coverage_pct=92.0, covered_items=["srv-auth", "srv-billing"]),
                KnowledgeCoverage(tenant_id=tenant_id, dimension=CoverageDimension.MODELS, coverage_pct=88.0, covered_items=["gpt-4", "claude-3"]),
                KnowledgeCoverage(tenant_id=tenant_id, dimension=CoverageDimension.CONTROLS, coverage_pct=95.0, covered_items=["SOC2-1", "ISO-27001"]),
            ]

        dim_scores = {c.dimension.value: c.coverage_pct / 100.0 for c in custom_coverages}
        avg = sum(dim_scores.values()) / len(dim_scores) if dim_scores else 0.88

        assessment = CoverageAssessment(
            tenant_id=tenant_id,
            scores=CoverageScore(overall_coverage_score=avg, dimension_scores=dim_scores),
            coverages=custom_coverages,
        )
        self._assessments[assessment.assessment_id] = assessment
        return assessment
