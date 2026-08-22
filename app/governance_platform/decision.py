"""Governance Decision Record Persistence & Model Definitions."""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.governance_platform.policy_evaluation import GovernanceDecision

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class GovernanceDecisionRecord(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:10]}")
    action: str
    target_resource_id: str
    tenant_id: str = "global"
    actor_id: str = "user"

    decision: GovernanceDecision = GovernanceDecision.ALLOW
    matched_policies: List[str] = Field(default_factory=list)
    violations: List[str] = Field(default_factory=list)
    risk_score: float = 0.0
    evidence_ids: List[str] = Field(default_factory=list)

    approved_by: Optional[str] = None
    approval_request_id: Optional[str] = None
    raw_explanation: str = ""
    timestamp: datetime = Field(default_factory=_now)
