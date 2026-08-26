"""Governed Knowledge Retrieval Subsystem (Phase 5.35)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.knowledge_intelligence.exceptions import (
    CrossTenantKnowledgeAccessException,
    KnowledgeRetrievalBlockedException,
    KnowledgeAccessDeniedException,
)
from app.knowledge_intelligence.knowledge import KnowledgeItem, KnowledgeClassification
from app.platform_contracts.redaction import SensitiveDataSanitizer


class RetrievalStrategy(str, Enum):
    EXACT = "EXACT"
    SEMANTIC = "SEMANTIC"
    GRAPH = "GRAPH"
    PROVENANCE = "PROVENANCE"
    HYBRID = "HYBRID"


class RetrievalConstraint(BaseModel):
    max_classification: KnowledgeClassification = KnowledgeClassification.CRITICAL
    require_provenance: bool = False
    min_trust_score: float = 0.0
    allowed_domains: Optional[List[str]] = None


class RetrievalEvidence(BaseModel):
    item_id: str
    relevance_score: float = 0.95
    trust_score: float = 90.0
    freshness_status: str = "FRESH"


class KnowledgeRetrievalRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"kretreq_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    user_id: str = "system"
    query: str
    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    constraints: RetrievalConstraint = Field(default_factory=RetrievalConstraint)


class RetrievalResult(BaseModel):
    request_id: str
    tenant_id: str
    items: List[KnowledgeItem] = Field(default_factory=list)
    evidences: List[RetrievalEvidence] = Field(default_factory=list)
    total_retrieved: int = 0
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class KnowledgeRetrievalManager:
    """Manages multi-tenant, policy-governed knowledge retrieval planning and result filtering."""

    def plan_and_retrieve(
        self,
        request: KnowledgeRetrievalRequest,
        candidate_items: List[KnowledgeItem],
        is_authorized: bool = True,
    ) -> RetrievalResult:
        if not is_authorized:
            raise KnowledgeAccessDeniedException("User not authorized for knowledge retrieval.")

        filtered_items = []
        evidences = []

        classification_hierarchy = {
            KnowledgeClassification.PUBLIC: 1,
            KnowledgeClassification.INTERNAL: 2,
            KnowledgeClassification.CONFIDENTIAL: 3,
            KnowledgeClassification.RESTRICTED: 4,
            KnowledgeClassification.CRITICAL: 5,
        }
        max_level = classification_hierarchy.get(request.constraints.max_classification, 5)

        for item in candidate_items:
            if item.tenant_id != request.tenant_id:
                raise CrossTenantKnowledgeAccessException(request.tenant_id)

            item_level = classification_hierarchy.get(item.classification, 2)
            if item_level > max_level:
                continue

            filtered_items.append(item)
            evidences.append(RetrievalEvidence(item_id=item.item_id))

        return RetrievalResult(
            request_id=request.request_id,
            tenant_id=request.tenant_id,
            items=filtered_items,
            evidences=evidences,
            total_retrieved=len(filtered_items),
        )
