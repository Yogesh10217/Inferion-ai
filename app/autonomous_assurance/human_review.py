"""
Human Review Ticket Subsystem.
Manages human reviewer ticket lifecycle and audit queues for workflow actions.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field


class HumanReviewStatus(str, Enum):
    PENDING = "PENDING"
    ASSIGNED = "ASSIGNED"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class AutonomousHumanReviewTicket(BaseModel):
    ticket_id: str = Field(default_factory=lambda: f"hrev_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    reviewer: Optional[str] = None
    status: HumanReviewStatus = HumanReviewStatus.PENDING
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None


class AutonomousHumanReviewEngine:
    """Manages human review tickets."""

    def __init__(self) -> None:
        self._tickets: Dict[str, AutonomousHumanReviewTicket] = {}

    def create_ticket(self, workflow_id: str, tenant_id: str, reviewer: Optional[str] = None) -> AutonomousHumanReviewTicket:
        t = AutonomousHumanReviewTicket(workflow_id=workflow_id, tenant_id=tenant_id, reviewer=reviewer)
        self._tickets[workflow_id] = t
        return t

    def resolve_ticket(self, workflow_id: str, tenant_id: str, reviewer: str, approved: bool, notes: Optional[str] = None) -> AutonomousHumanReviewTicket:
        t = self._tickets.get(workflow_id) or self.create_ticket(workflow_id, tenant_id, reviewer)
        t.reviewer = reviewer
        t.status = HumanReviewStatus.APPROVED if approved else HumanReviewStatus.REJECTED
        t.notes = notes
        t.resolved_at = datetime.now(timezone.utc)
        return t

    def get_ticket(self, workflow_id: str) -> Optional[AutonomousHumanReviewTicket]:
        return self._tickets.get(workflow_id)
