"""Standardized Governance Decision Contract (Phase 5.30)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class GovernanceDecisionStatus(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class GovernanceDecisionReason(BaseModel):
    code: str
    message: str
    severity: str = "INFO"


class PolicyReference(BaseModel):
    policy_id: str
    policy_name: str
    policy_version: str = "1.0.0"


class GovernanceDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"govdec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    subject_type: str
    subject_id: str
    status: GovernanceDecisionStatus = GovernanceDecisionStatus.ALLOW
    reasons: List[GovernanceDecisionReason] = Field(default_factory=list)
    policy_references: List[PolicyReference] = Field(default_factory=list)
    risk_reference_id: Optional[str] = None
    trust_reference_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0.0"
