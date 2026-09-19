"""
Human Review Lifecycle Subsystem.
Tracks human reviewer assignment, review queues, audit trails, and feedback loops for decision intelligence recommendations.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field


class DecisionHumanReviewTicket(BaseModel):
    ticket_id: str = Field(default_factory=lambda: f"rev_{uuid.uuid4().hex[:12]}")
    decision_id: str
    tenant_id: str
    reviewer: Optional[str] = None
    status: str = "PENDING_REVIEW"
    review_notes: Optional[str] = None
    assigned_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class DecisionHumanReviewEngine:
    """Manages human review tickets and queues for decisions."""

    def __init__(self) -> None:
        self._tickets: Dict[str, DecisionHumanReviewTicket] = {}

    def create_review_ticket(
        self, decision_id: str, tenant_id: str, reviewer: Optional[str] = None
    ) -> DecisionHumanReviewTicket:
        ticket = DecisionHumanReviewTicket(decision_id=decision_id, tenant_id=tenant_id, reviewer=reviewer)
        self._tickets[decision_id] = ticket
        return ticket

    def complete_review(
        self,
        decision_id: str,
        tenant_id: str,
        reviewer: str,
        status: str = "COMPLETED",
        review_notes: Optional[str] = None,
    ) -> DecisionHumanReviewTicket:
        ticket = self._tickets.get(decision_id) or self.create_review_ticket(decision_id, tenant_id, reviewer)
        ticket.reviewer = reviewer
        ticket.status = status
        ticket.review_notes = review_notes
        ticket.completed_at = datetime.now(timezone.utc)
        return ticket

    def get_review_ticket(self, decision_id: str) -> Optional[DecisionHumanReviewTicket]:
        return self._tickets.get(decision_id)
