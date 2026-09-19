"""Recommendation intelligence for generating explainable, evidence-backed decision proposals."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.decision_governance.exceptions import (
    CrossTenantDecisionGovernanceException,
    RecommendationNotFoundException,
)


class RecommendationType(str, Enum):
    ACTION = "ACTION"
    PREVENTION = "PREVENTION"
    OPTIMIZATION = "OPTIMIZATION"
    MITIGATION = "MITIGATION"
    ESCALATION = "ESCALATION"
    INVESTIGATION = "INVESTIGATION"


class RecommendationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecommendationConfidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"


class RecommendationStatus(str, Enum):
    PROPOSED = "PROPOSED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


class RecommendationEvidence(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_domain: str
    description: str
    confidence_score: float = 1.0
    fingerprint: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    decision_id: str
    tenant_id: str
    title: str
    description: str
    recommendation_type: RecommendationType = RecommendationType.ACTION
    priority: RecommendationPriority = RecommendationPriority.MEDIUM
    confidence: RecommendationConfidence = RecommendationConfidence.HIGH
    confidence_score: float = 0.85
    expected_impact_score: float = 0.80
    status: RecommendationStatus = RecommendationStatus.PROPOSED
    evidence_list: List[RecommendationEvidence] = Field(default_factory=list)
    rationale: str = ""
    tradeoffs: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DecisionRecommendationManager:
    """Manages advisory decision recommendations."""

    def __init__(self) -> None:
        self._recommendations: Dict[str, DecisionRecommendation] = {}

    def create_recommendation(
        self,
        tenant_id: str,
        decision_id: str,
        title: str,
        description: str,
        rationale: str,
        recommendation_type: RecommendationType = RecommendationType.ACTION,
        priority: RecommendationPriority = RecommendationPriority.MEDIUM,
        confidence: RecommendationConfidence = RecommendationConfidence.HIGH,
        confidence_score: float = 0.85,
        expected_impact_score: float = 0.80,
        evidence_list: Optional[List[RecommendationEvidence]] = None,
        tradeoffs: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DecisionRecommendation:
        rec = DecisionRecommendation(
            tenant_id=tenant_id,
            decision_id=decision_id,
            title=title,
            description=description,
            rationale=rationale,
            recommendation_type=recommendation_type,
            priority=priority,
            confidence=confidence,
            confidence_score=confidence_score,
            expected_impact_score=expected_impact_score,
            evidence_list=evidence_list or [],
            tradeoffs=tradeoffs or [],
            metadata=metadata or {},
        )
        self._recommendations[rec.recommendation_id] = rec
        return rec

    def get_recommendation(self, recommendation_id: str, tenant_id: str) -> DecisionRecommendation:
        rec = self._recommendations.get(recommendation_id)
        if not rec:
            raise RecommendationNotFoundException(f"Recommendation '{recommendation_id}' not found")
        if rec.tenant_id != tenant_id:
            raise CrossTenantDecisionGovernanceException()
        return rec

    def list_recommendations_for_decision(self, decision_id: str, tenant_id: str) -> List[DecisionRecommendation]:
        recs = [r for r in self._recommendations.values() if r.decision_id == decision_id and r.tenant_id == tenant_id]
        return sorted(recs, key=lambda x: (x.confidence_score * x.expected_impact_score), reverse=True)

    def update_status(
        self, recommendation_id: str, tenant_id: str, status: RecommendationStatus
    ) -> DecisionRecommendation:
        rec = self.get_recommendation(recommendation_id, tenant_id)
        rec.status = status
        return rec
