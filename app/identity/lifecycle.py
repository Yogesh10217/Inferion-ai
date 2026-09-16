"""Identity Lifecycle Automation & Periodic Access Review Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ReviewStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REVOKED = "REVOKED"
    EXPIRED = "EXPIRED"


class AccessReview(BaseModel):
    review_id: str = Field(default_factory=lambda: f"rev_{uuid.uuid4().hex[:10]}")
    identity_id: str
    tenant_id: str = "global"

    role: str
    status: ReviewStatus = ReviewStatus.PENDING
    reviewer_id: Optional[str] = None
    created_at: datetime = Field(default_factory=_now)


class IdentityLifecycleManager:
    """Manages periodic access reviews, stale credential detection, and identity lifecycle automation."""

    def __init__(self) -> None:
        self._reviews: Dict[str, AccessReview] = {}

    def initiate_access_review(self, identity_id: str, role: str, tenant_id: str = "global") -> AccessReview:
        rev = AccessReview(identity_id=identity_id, role=role, tenant_id=tenant_id)
        self._reviews[rev.review_id] = rev
        logger.info(f"[IDENTITY LIFECYCLE] Initiated access review '{rev.review_id}' for identity '{identity_id}' (Role: {role})")
        return rev

    def certify_access(self, review_id: str, reviewer_id: str) -> AccessReview:
        rev = self.get_review(review_id)
        rev.status = ReviewStatus.APPROVED
        rev.reviewer_id = reviewer_id
        logger.info(f"[IDENTITY LIFECYCLE] Certified access review '{review_id}' by '{reviewer_id}'")
        return rev

    def get_review(self, review_id: str) -> AccessReview:
        rev = self._reviews.get(review_id)
        if not rev:
            raise KeyError(f"Access review '{review_id}' not found")
        return rev
