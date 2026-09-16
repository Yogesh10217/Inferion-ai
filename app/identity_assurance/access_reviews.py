"""Enterprise Access Review Intelligence."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import (
    CrossTenantIdentityAssuranceException,
)


class AccessReviewStatus(str, Enum):
    DRAFT = "DRAFT"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"


class AccessReviewScope(BaseModel):
    review_type: str = "PRIVILEGED_ACCESS"  # PERIODIC, PRIVILEGED_ACCESS, AGENT_ACCESS, SERVICE_ACCOUNT
    target_identities: List[str] = Field(default_factory=list)
    due_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessReviewFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    decision: str = "CERTIFIED"  # CERTIFIED, REVOKE, MODIFY
    reviewer_notes: str = ""


class AccessReview(BaseModel):
    review_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    title: str
    scope: AccessReviewScope = Field(default_factory=AccessReviewScope)
    status: AccessReviewStatus = AccessReviewStatus.IN_PROGRESS
    findings: List[AccessReviewFinding] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessReviewManager:
    """Manages periodic, privileged, agent, and service account access reviews."""

    def __init__(self) -> None:
        self._reviews: Dict[str, AccessReview] = {}

    def create_review(
        self,
        tenant_id: str,
        title: str,
        review_type: str = "PRIVILEGED_ACCESS",
        target_identities: Optional[List[str]] = None,
    ) -> AccessReview:
        scope = AccessReviewScope(
            review_type=review_type,
            target_identities=target_identities or [],
        )
        review = AccessReview(
            tenant_id=tenant_id,
            title=title,
            scope=scope,
        )
        self._reviews[review.review_id] = review
        return review

    def get_review(self, tenant_id: str, review_id: str) -> AccessReview:
        review = self._reviews.get(review_id)
        if not review or review.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return review

    def add_finding(
        self,
        tenant_id: str,
        review_id: str,
        identity_id: str,
        decision: str = "CERTIFIED",
        notes: str = "",
    ) -> AccessReviewFinding:
        review = self.get_review(tenant_id, review_id)
        finding = AccessReviewFinding(
            identity_id=identity_id,
            decision=decision,
            reviewer_notes=notes,
        )
        review.findings.append(finding)
        return finding
