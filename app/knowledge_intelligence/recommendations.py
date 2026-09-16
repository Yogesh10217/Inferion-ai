"""Knowledge Recommendation Engine Subsystem (Phase 5.35)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.redaction import SensitiveDataSanitizer


class KnowledgeRecommendationType(str, Enum):
    REVALIDATE_KNOWLEDGE = "REVALIDATE_KNOWLEDGE"
    RESOLVE_CONTRADICTION = "RESOLVE_CONTRADICTION"
    UPDATE_REFERENCE = "UPDATE_REFERENCE"
    LINK_RELATED_KNOWLEDGE = "LINK_RELATED_KNOWLEDGE"
    RETIRE_STALE_KNOWLEDGE = "RETIRE_STALE_KNOWLEDGE"
    ESCALATE_FOR_REVIEW = "ESCALATE_FOR_REVIEW"
    IMPROVE_PROVENANCE = "IMPROVE_PROVENANCE"
    CREATE_POLICY_REVIEW = "CREATE_POLICY_REVIEW"


class RecommendationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecommendationConfidence(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class RecommendationStatus(str, Enum):
    PROPOSED = "PROPOSED"
    UNDER_REVIEW = "UNDER_REVIEW"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class KnowledgeRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"krec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_id: str
    recommendation_type: KnowledgeRecommendationType
    priority: RecommendationPriority = RecommendationPriority.MEDIUM
    confidence: RecommendationConfidence = RecommendationConfidence.HIGH
    status: RecommendationStatus = RecommendationStatus.PROPOSED
    title: str
    rationale: str
    is_high_risk: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeRecommendationEngine:
    """Generates non-mutating knowledge intelligence recommendations for governance and curation."""

    def __init__(self) -> None:
        self._recommendations: Dict[str, KnowledgeRecommendation] = {}

    def create_recommendation(
        self,
        tenant_id: str,
        target_id: str,
        title: str,
        rationale: str,
        recommendation_type: KnowledgeRecommendationType = KnowledgeRecommendationType.REVALIDATE_KNOWLEDGE,
        priority: RecommendationPriority = RecommendationPriority.MEDIUM,
        is_high_risk: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> KnowledgeRecommendation:
        sanitized_meta = SensitiveDataSanitizer.sanitize(metadata or {})
        rec = KnowledgeRecommendation(
            tenant_id=tenant_id,
            target_id=target_id,
            recommendation_type=recommendation_type,
            priority=priority,
            title=title,
            rationale=rationale,
            is_high_risk=is_high_risk,
            metadata=sanitized_meta if isinstance(sanitized_meta, dict) else {},
        )
        self._recommendations[rec.recommendation_id] = rec
        return rec

    def list_recommendations(self, tenant_id: str) -> List[KnowledgeRecommendation]:
        return [r for r in self._recommendations.values() if r.tenant_id == tenant_id]
