"""Human Decision Collaboration & Approval Integration."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.intelligence_platform.exceptions import IntelligenceException
from app.intelligence_platform.recommendations import Recommendation

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ReviewAction(str, Enum):
    APPROVE = "APPROVE"
    REJECT = "REJECT"
    REQUEST_MORE_INFORMATION = "REQUEST_MORE_INFORMATION"
    MODIFY_RECOMMENDATION = "MODIFY_RECOMMENDATION"
    ESCALATE = "ESCALATE"
    DEFER = "DEFER"


class DecisionReviewer(BaseModel):
    user_id: str
    role: str = "administrator"
    email: Optional[str] = None


class DecisionFeedback(BaseModel):
    feedback_id: str = Field(default_factory=lambda: f"fb_{uuid.uuid4().hex[:10]}")
    reviewer: DecisionReviewer
    action: ReviewAction
    comments: str = ""
    override_reason: Optional[str] = None
    submitted_at: datetime = Field(default_factory=_now)


class DecisionReview(BaseModel):
    review_id: str = Field(default_factory=lambda: f"rev_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    recommendation_id: str
    approval_request_id: Optional[str] = None
    status: str = "PENDING"
    feedbacks: List[DecisionFeedback] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)


class DecisionApprovalManager:
    """Manages human reviews and integrates with core ApprovalEngine."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self._reviews: Dict[str, DecisionReview] = {}

    def request_human_approval(
        self,
        tenant_id: str,
        recommendation: Recommendation,
        requester: str = "IntelligencePlatform",
    ) -> DecisionReview:
        # Request approval from core ApprovalEngine
        appr_req = self.approval_engine.request_approval(
            execution_id=recommendation.recommendation_id,
            action_type=recommendation.recommendation_type.value,
            requester=requester,
            tenant_id=tenant_id,
            payload={
                "title": recommendation.title,
                "target_resource_id": recommendation.target_resource_id,
                "risk_level": recommendation.risk_level,
                "action_description": recommendation.action_description,
            },
        )

        rev = DecisionReview(
            tenant_id=tenant_id,
            recommendation_id=recommendation.recommendation_id,
            approval_request_id=appr_req.request_id,
            status="PENDING",
        )
        self._reviews[rev.review_id] = rev
        logger.info(f"[DECISION APPROVAL MANAGER] Requested human approval for recommendation '{recommendation.recommendation_id}' (Approval ID: '{appr_req.request_id}')")
        return rev

    def submit_review_decision(
        self,
        tenant_id: str,
        review_id: str,
        reviewer: DecisionReviewer,
        action: ReviewAction,
        comments: str = "",
    ) -> DecisionReview:
        rev = self._reviews.get(review_id)
        if not rev or rev.tenant_id != tenant_id:
            raise IntelligenceException(f"Decision review '{review_id}' not found for tenant '{tenant_id}'.")

        fb = DecisionFeedback(reviewer=reviewer, action=action, comments=comments)
        rev.feedbacks.append(fb)

        if action == ReviewAction.APPROVE:
            rev.status = "APPROVED"
            if rev.approval_request_id:
                self.approval_engine.approve(rev.approval_request_id, approver_id=reviewer.user_id)
        elif action == ReviewAction.REJECT:
            rev.status = "REJECTED"
        else:
            rev.status = action.value

        logger.info(f"[DECISION APPROVAL MANAGER] Review '{review_id}' updated to {rev.status} by '{reviewer.user_id}'")
        return rev
