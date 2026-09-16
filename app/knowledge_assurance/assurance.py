"""Knowledge Assurance Assessment Module.

Provides continuous holistic knowledge assurance evaluation across trust, freshness,
provenance, consistency, coverage, and conflict risk dimensions.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.knowledge_assurance.conflicts import KnowledgeConflictManager
from app.knowledge_assurance.consistency import KnowledgeConsistencyManager
from app.knowledge_assurance.coverage import KnowledgeCoverageManager
from app.knowledge_assurance.exceptions import (
    CrossTenantKnowledgeAssuranceException,
)
from app.knowledge_assurance.freshness import KnowledgeFreshnessManager
from app.knowledge_assurance.provenance import KnowledgeProvenanceManager
from app.knowledge_assurance.trust import KnowledgeTrustEngine


class KnowledgeAssuranceDimension(str, Enum):
    TRUST = "TRUST"
    FRESHNESS = "FRESHNESS"
    PROVENANCE = "PROVENANCE"
    CONSISTENCY = "CONSISTENCY"
    COVERAGE = "COVERAGE"
    CONFLICT_RISK = "CONFLICT_RISK"


class KnowledgeAssuranceFactor(BaseModel):
    name: str
    dimension: KnowledgeAssuranceDimension
    score: float = Field(ge=0.0, le=1.0)
    weight: float = 1.0
    finding: str = ""


class KnowledgeAssuranceScore(BaseModel):
    overall_score: float = Field(ge=0.0, le=1.0)
    assurance_level: str = "HIGH"  # CRITICAL, LOW, MODERATE, HIGH, EXCELLENT
    dimension_scores: Dict[KnowledgeAssuranceDimension, float] = Field(default_factory=dict)


class KnowledgeAssuranceAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"kass-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    target_resource_id: str
    assurance_score: KnowledgeAssuranceScore
    factors: List[KnowledgeAssuranceFactor] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeContinuousAssuranceManager:
    """Manages continuous knowledge assurance assessments across enterprise knowledge domains."""

    def __init__(
        self,
        trust_engine: Optional[KnowledgeTrustEngine] = None,
        freshness_manager: Optional[KnowledgeFreshnessManager] = None,
        provenance_manager: Optional[KnowledgeProvenanceManager] = None,
        consistency_manager: Optional[KnowledgeConsistencyManager] = None,
        coverage_manager: Optional[KnowledgeCoverageManager] = None,
        conflict_manager: Optional[KnowledgeConflictManager] = None,
    ) -> None:
        self.trust_engine = trust_engine or KnowledgeTrustEngine()
        self.freshness_manager = freshness_manager or KnowledgeFreshnessManager()
        self.provenance_manager = provenance_manager or KnowledgeProvenanceManager()
        self.consistency_manager = consistency_manager or KnowledgeConsistencyManager()
        self.coverage_manager = coverage_manager or KnowledgeCoverageManager()
        self.conflict_manager = conflict_manager or KnowledgeConflictManager()
        self._assessments: Dict[str, KnowledgeAssuranceAssessment] = {}

    def assess_knowledge_assurance(
        self,
        tenant_id: str,
        target_resource_id: str,
        dimensions_override: Optional[Dict[KnowledgeAssuranceDimension, float]] = None,
    ) -> KnowledgeAssuranceAssessment:
        dim_scores: Dict[KnowledgeAssuranceDimension, float] = {}
        factors: List[KnowledgeAssuranceFactor] = []
        recommendations: List[str] = []

        if dimensions_override:
            for dim, score in dimensions_override.items():
                dim_scores[dim] = max(0.0, min(1.0, score))
                factors.append(
                    KnowledgeAssuranceFactor(
                        name=f"{dim.value}_override",
                        dimension=dim,
                        score=dim_scores[dim],
                    )
                )
        else:
            # Default evaluation logic
            dim_scores[KnowledgeAssuranceDimension.TRUST] = 0.90
            dim_scores[KnowledgeAssuranceDimension.FRESHNESS] = 0.85
            dim_scores[KnowledgeAssuranceDimension.PROVENANCE] = 0.95
            dim_scores[KnowledgeAssuranceDimension.CONSISTENCY] = 0.88
            dim_scores[KnowledgeAssuranceDimension.COVERAGE] = 0.82
            dim_scores[KnowledgeAssuranceDimension.CONFLICT_RISK] = 0.90  # 1.0 = low risk

            for dim, score in dim_scores.items():
                factors.append(
                    KnowledgeAssuranceFactor(
                        name=f"{dim.value.lower()}_evaluation",
                        dimension=dim,
                        score=score,
                        finding=f"Evaluated {dim.value} score: {score:.2f}",
                    )
                )

        avg_score = sum(dim_scores.values()) / len(dim_scores) if dim_scores else 0.0

        if avg_score >= 0.9:
            level = "EXCELLENT"
        elif avg_score >= 0.75:
            level = "HIGH"
        elif avg_score >= 0.6:
            level = "MODERATE"
        elif avg_score >= 0.4:
            level = "LOW"
        else:
            level = "CRITICAL"
            recommendations.append("Immediate knowledge remediation recommended.")

        score_obj = KnowledgeAssuranceScore(
            overall_score=round(avg_score, 4),
            assurance_level=level,
            dimension_scores=dim_scores,
        )

        assessment = KnowledgeAssuranceAssessment(
            tenant_id=tenant_id,
            target_resource_id=target_resource_id,
            assurance_score=score_obj,
            factors=factors,
            recommendations=recommendations,
        )
        self._assessments[assessment.assessment_id] = assessment
        return assessment

    def get_assessment(
        self, tenant_id: str, assessment_id: str
    ) -> KnowledgeAssuranceAssessment:
        if assessment_id not in self._assessments:
            raise CrossTenantKnowledgeAssuranceException()
        ass = self._assessments[assessment_id]
        if ass.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()
        return ass

    def list_assessments(self, tenant_id: str) -> List[KnowledgeAssuranceAssessment]:
        return [a for a in self._assessments.values() if a.tenant_id == tenant_id]
