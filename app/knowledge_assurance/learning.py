"""Knowledge Assurance Advisory Learning Module.

Provides advisory knowledge learning recommendations.
MANDATORY: auto_execute = False is strictly enforced on all learning recommendations.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.knowledge_assurance.exceptions import (
    CrossTenantKnowledgeAssuranceException,
    KnowledgeReferenceNotFoundException,
)


class KnowledgeLearningPattern(BaseModel):
    pattern_id: str = Field(default_factory=lambda: f"pat-{uuid.uuid4().hex[:8]}")
    pattern_name: str
    description: str
    frequency: int = 1
    confidence: float = 0.8
    associated_domains: List[str] = Field(default_factory=list)


class KnowledgeLearningRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"rec-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    title: str
    description: str
    action_type: str
    target_resource_id: str
    auto_execute: bool = False  # MANDATORY INVARIANT: Always False
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        # Enforce invariant
        if self.auto_execute is not False:
            object.__setattr__(self, "auto_execute", False)


class KnowledgeLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"klr-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    source_event: str
    patterns_identified: List[KnowledgeLearningPattern] = Field(default_factory=list)
    recommendations: List[KnowledgeLearningRecommendation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeLearningManager:
    """Manages advisory knowledge learning records and recommendations."""

    def __init__(self) -> None:
        self._records: Dict[str, KnowledgeLearningRecord] = {}

    def record_learning_event(
        self,
        tenant_id: str,
        source_event: str,
        patterns: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
    ) -> KnowledgeLearningRecord:
        pat_objs = [
            KnowledgeLearningPattern(
                pattern_name=p.get("pattern_name", "UNKNOWN"),
                description=p.get("description", ""),
                frequency=p.get("frequency", 1),
                confidence=p.get("confidence", 0.8),
                associated_domains=p.get("associated_domains", []),
            )
            for p in patterns
        ]

        rec_objs = [
            KnowledgeLearningRecommendation(
                tenant_id=tenant_id,
                title=r.get("title", "Recommendation"),
                description=r.get("description", ""),
                action_type=r.get("action_type", "OPTIMIZE_KNOWLEDGE"),
                target_resource_id=r.get("target_resource_id", "GLOBAL"),
                auto_execute=False,  # ALWAYS False
                payload=r.get("payload", {}),
            )
            for r in recommendations
        ]

        rec = KnowledgeLearningRecord(
            tenant_id=tenant_id,
            source_event=source_event,
            patterns_identified=pat_objs,
            recommendations=rec_objs,
        )
        self._records[rec.record_id] = rec
        return rec

    def get_record(self, tenant_id: str, record_id: str) -> KnowledgeLearningRecord:
        if record_id not in self._records:
            raise KnowledgeReferenceNotFoundException(f"Learning record {record_id} not found.")
        rec = self._records[record_id]
        if rec.tenant_id != tenant_id:
            raise CrossTenantKnowledgeAssuranceException()
        return rec

    def list_records(self, tenant_id: str) -> List[KnowledgeLearningRecord]:
        return [r for r in self._records.values() if r.tenant_id == tenant_id]

    def list_recommendations(
        self, tenant_id: str
    ) -> List[KnowledgeLearningRecommendation]:
        recs: List[KnowledgeLearningRecommendation] = []
        for r in self.list_records(tenant_id):
            recs.extend(r.recommendations)
        return recs
