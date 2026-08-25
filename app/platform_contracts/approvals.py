"""Shared Approval Reference Contract (Phase 5.30)."""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine


class ApprovalStatusReference(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


class ApprovalRequirement(BaseModel):
    action_type: str
    required_approver_role: str = "ADMIN"
    reason: str


class ApprovalReference(BaseModel):
    approval_id: str
    tenant_id: str
    action_type: str
    approval_status: ApprovalStatusReference = ApprovalStatusReference.PENDING
    requested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None
