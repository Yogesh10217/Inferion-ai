"""
Human Approval Request Entity Representation
"""

import time
import uuid
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_policies import RiskLevel


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    ESCALATED = "ESCALATED"


class ApprovalRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"appr_{uuid.uuid4().hex[:10]}")
    execution_id: str
    tenant_id: str = "default_tenant"
    requester: str = "autonomous_agent"
    approver: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM
    action_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: float = Field(default_factory=time.time)
    resolved_at: Optional[float] = None
