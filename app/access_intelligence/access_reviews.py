"""Continuous Access Review Lifecycle (Phase 5.39)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.access_intelligence.exceptions import (
    CrossTenantAccessIntelligenceException,
    ImmutableAccessRecordException,
    InvalidAccessStateTransitionException,
)


class AccessReviewScope(str, Enum):
    TENANT = "TENANT"
    WORKSPACE = "WORKSPACE"
    RESOURCE = "RESOURCE"
    IDENTITY = "IDENTITY"
    ROLE = "ROLE"


class AccessReviewStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    REVIEWING = "REVIEWING"
    DECIDED = "DECIDED"
    FINALIZED = "FINALIZED"


class AccessReviewDecision(str, Enum):
    MAINTAIN = "MAINTAIN"
    REVOKE = "REVOKE"
    MODIFY = "MODIFY"


class AccessReview(BaseModel):
    """Access Review representation."""
    review_id: str = Field(default_factory=lambda: f"ar_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    title: str
    reviewer_identity_id: str
    target_identity_id: str
    target_entitlement_id: str
    scope: AccessReviewScope = AccessReviewScope.IDENTITY
    status: AccessReviewStatus = AccessReviewStatus.DRAFT
    decision: Optional[AccessReviewDecision] = None
    justification: str = ""
    is_finalized: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finalized_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AccessReviewManager:
    """Manages continuous access review lifecycle."""

    def __init__(self) -> None:
        self._reviews: Dict[str, AccessReview] = {}

    def create_review(
        self,
        tenant_id: str,
        title: str,
        reviewer_identity_id: str,
        target_identity_id: str,
        target_entitlement_id: str,
        scope: AccessReviewScope = AccessReviewScope.IDENTITY,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AccessReview:
        rev = AccessReview(
            tenant_id=tenant_id,
            title=title,
            reviewer_identity_id=reviewer_identity_id,
            target_identity_id=target_identity_id,
            target_entitlement_id=target_entitlement_id,
            scope=scope,
            metadata=metadata or {},
        )
        self._reviews[rev.review_id] = rev
        return rev

    def activate_review(self, tenant_id: str, review_id: str) -> AccessReview:
        rev = self.get_review(tenant_id, review_id)
        if rev.status != AccessReviewStatus.DRAFT:
            raise InvalidAccessStateTransitionException(rev.status.value, AccessReviewStatus.ACTIVE.value)
        rev.status = AccessReviewStatus.ACTIVE
        return rev

    def start_reviewing(self, tenant_id: str, review_id: str) -> AccessReview:
        rev = self.get_review(tenant_id, review_id)
        if rev.status != AccessReviewStatus.ACTIVE:
            raise InvalidAccessStateTransitionException(rev.status.value, AccessReviewStatus.REVIEWING.value)
        rev.status = AccessReviewStatus.REVIEWING
        return rev

    def record_decision(self, tenant_id: str, review_id: str, decision: AccessReviewDecision, justification: str) -> AccessReview:
        rev = self.get_review(tenant_id, review_id)
        if rev.is_finalized:
            raise ImmutableAccessRecordException(review_id)
        rev.decision = decision
        rev.justification = justification
        rev.status = AccessReviewStatus.DECIDED
        return rev

    def finalize_review(self, tenant_id: str, review_id: str) -> AccessReview:
        rev = self.get_review(tenant_id, review_id)
        if rev.status != AccessReviewStatus.DECIDED:
            raise InvalidAccessStateTransitionException(rev.status.value, AccessReviewStatus.FINALIZED.value)
        rev.status = AccessReviewStatus.FINALIZED
        rev.is_finalized = True
        rev.finalized_at = datetime.now(timezone.utc)
        return rev

    def get_review(self, tenant_id: str, review_id: str) -> AccessReview:
        rev = self._reviews.get(review_id)
        if not rev or rev.tenant_id != tenant_id:
            raise CrossTenantAccessIntelligenceException()
        return rev

    def list_reviews(self, tenant_id: str, status: Optional[AccessReviewStatus] = None) -> List[AccessReview]:
        results = [r for r in self._reviews.values() if r.tenant_id == tenant_id]
        if status:
            results = [r for r in results if r.status == status]
        return results
