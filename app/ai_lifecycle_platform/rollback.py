"""Controlled Rollback Governance Subsystem (Phase 5.33)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.approvals.approval_engine import ApprovalEngine
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget
from app.platform_contracts.idempotency import IdempotencyManager


class RollbackStatus(str, Enum):
    REQUESTED = "REQUESTED"
    EVALUATING = "EVALUATING"
    APPROVED = "APPROVED"
    DELEGATED = "DELEGATED"
    COMPLETED = "COMPLETED"


class RollbackDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"rbdec_{uuid.uuid4().hex[:12]}")
    status: RollbackStatus = RollbackStatus.APPROVED
    reason: str = "Rollback approved"


class RollbackPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"rbplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    target_version: str
    delegation_request: DelegationRequest


class RollbackRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"rbreq_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    target_version: str
    reason: str = "High severity drift detected"
    status: RollbackStatus = RollbackStatus.REQUESTED
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RollbackManager:
    """Manages rollback governance delegating execution strictly via DelegationRequest."""

    def __init__(
        self,
        approval_engine: Optional[ApprovalEngine] = None,
        idempotency_manager: Optional[IdempotencyManager] = None,
    ) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self.idempotency_manager = idempotency_manager or IdempotencyManager()
        self._requests: Dict[str, RollbackRequest] = {}

    def request_rollback(
        self,
        tenant_id: str,
        asset_id: str,
        target_version: str,
        reason: str = "High severity drift",
        requires_approval: bool = False,
    ) -> RollbackRequest:
        req = RollbackRequest(
            tenant_id=tenant_id,
            asset_id=asset_id,
            target_version=target_version,
            reason=reason,
        )

        if requires_approval:
            req.status = RollbackStatus.EVALUATING
            self.approval_engine.request_approval(
                execution_id=req.request_id,
                action_type="HIGH_IMPACT_ROLLBACK",
                tenant_id=tenant_id,
                requester="ai_lifecycle_platform",
            )
        else:
            req.status = RollbackStatus.APPROVED

        self._requests[req.request_id] = req
        return req

    def execute_rollback_plan(self, req: RollbackRequest) -> RollbackPlan:
        delegation = DelegationRequest(
            tenant_id=req.tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action="ROLLBACK_AI_ASSET",
            payload={"asset_id": req.asset_id, "target_version": req.target_version},
        )
        return RollbackPlan(
            tenant_id=req.tenant_id,
            asset_id=req.asset_id,
            target_version=req.target_version,
            delegation_request=delegation,
        )
