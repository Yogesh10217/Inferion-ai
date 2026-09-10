"""Runtime human review engine for Runtime Intelligence (Phase 5.57)."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from app.runtime_intelligence.models import RuntimeHumanReviewState
from app.runtime_intelligence.exceptions import (
    CrossTenantRuntimeIntelligenceException,
    RuntimeIntelligenceException,
)

logger = logging.getLogger(__name__)


class RuntimeHumanReviewEngine:
    """Manages human review lifecycle for runtime intelligence proposals and delegations."""

    def __init__(self) -> None:
        self._reviews: Dict[str, Dict[str, Any]] = {}

    def submit_for_review(
        self, tenant_id: str, action_id: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        review_id = f"rev_{uuid.uuid4().hex[:12]}"
        review = {
            "review_id": review_id,
            "tenant_id": tenant_id,
            "action_id": action_id,
            "state": RuntimeHumanReviewState.PENDING.value,
            "context": context or {},
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "decision": None,
            "reviewer_id": None,
            "justification": "",
        }
        self._reviews[review_id] = review
        logger.info(f"Submitted action '{action_id}' for human review (Review ID: {review_id})")
        return review

    def record_decision(
        self,
        tenant_id: str,
        review_id: str,
        reviewer_id: str,
        decision: str,
        justification: str = "",
    ) -> Dict[str, Any]:
        rev = self._reviews.get(review_id)
        if not rev:
            raise RuntimeIntelligenceException("Human review record not found")
        if rev["tenant_id"] != tenant_id:
            raise CrossTenantRuntimeIntelligenceException()

        rev["decision"] = decision
        rev["reviewer_id"] = reviewer_id
        rev["justification"] = justification
        rev["state"] = RuntimeHumanReviewState.APPROVED.value if decision.upper() == "APPROVED" else RuntimeHumanReviewState.REJECTED.value
        rev["reviewed_at"] = datetime.now(timezone.utc).isoformat()
        logger.info(f"Recorded human review decision '{decision}' for review '{review_id}' by '{reviewer_id}'")
        return rev

    def escalate_review(
        self, tenant_id: str, review_id: str, escalation_reason: str
    ) -> Dict[str, Any]:
        rev = self._reviews.get(review_id)
        if not rev:
            raise RuntimeIntelligenceException("Human review record not found")
        if rev["tenant_id"] != tenant_id:
            raise CrossTenantRuntimeIntelligenceException()

        rev["state"] = RuntimeHumanReviewState.ESCALATED.value
        rev["escalation_reason"] = escalation_reason
        logger.info(f"Escalated human review '{review_id}': {escalation_reason}")
        return rev

    def get_review(self, tenant_id: str, review_id: str) -> Optional[Dict[str, Any]]:
        rev = self._reviews.get(review_id)
        if rev and rev["tenant_id"] != tenant_id:
            raise CrossTenantRuntimeIntelligenceException()
        return rev
