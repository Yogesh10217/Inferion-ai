"""
Autonomous Delegation Coordinator Subsystem.
Constructs formal DelegationRequest contracts for downstream execution platforms.
NEVER mutates external infrastructure directly.
"""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.autonomous_assurance.exceptions import (
    HighRiskAutonomousActionRequiresApprovalException,
)
from app.platform_contracts.delegation import DelegationRequest, DelegationTarget

logger = logging.getLogger(__name__)


class DelegationPlanStatus(str, Enum):
    PENDING = "PENDING"
    DELEGATED = "DELEGATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class DelegationPlan(BaseModel):
    delegation_id: str = Field(default_factory=lambda: f"autodel_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    target_subsystem: str = "OPERATIONS"
    action_type: str = "RESTART_SERVICE"
    status: DelegationPlanStatus = DelegationPlanStatus.PENDING
    parameters: Dict[str, Any] = Field(default_factory=dict)
    delegation_request: Optional[DelegationRequest] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def request_id(self) -> str:
        if self.delegation_request:
            req_id = getattr(self.delegation_request, "delegation_id", getattr(self.delegation_request, "request_id", None))
            if req_id and req_id.startswith("del_req_"):
                return req_id
        clean_id = self.delegation_id[8:] if self.delegation_id.startswith("autodel_") else self.delegation_id
        return f"del_req_{clean_id}"

    @property
    def target_provider(self) -> str:
        return self.target_subsystem


class AutonomousDelegationCoordinator:
    """Coordinates delegation request creation without executing mutations directly."""

    def __init__(self) -> None:
        self._delegations: Dict[str, DelegationPlan] = {}

    def create_delegation_request(
        self,
        workflow_id: str,
        tenant_id: str,
        target_subsystem: str = "OPERATIONS",
        action_type: str = "RESTART_SERVICE",
        parameters: Optional[Dict[str, Any]] = None,
        is_approved: bool = True,
        target_provider: Optional[str] = None,
    ) -> DelegationPlan:
        subsystem = target_provider or target_subsystem
        if not is_approved and ("RESTART" in action_type or "DISABLE" in action_type or "SCALE" in action_type):
            raise HighRiskAutonomousActionRequiresApprovalException(
                f"High-risk action '{action_type}' requires human approval before delegation for workflow '{workflow_id}'."
            )

        req = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action=action_type,
            payload=parameters or {},
        )

        plan = DelegationPlan(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            target_subsystem=subsystem,
            action_type=action_type,
            parameters=parameters or {},
            delegation_request=req,
        )
        self._delegations[workflow_id] = plan
        logger.info(f"[DELEGATION COORDINATOR] Produced DelegationRequest '{req.delegation_id}' for workflow '{workflow_id}'. Zero direct execution.")
        return plan

    def get_delegation(self, workflow_id: str) -> Optional[DelegationPlan]:
        return self._delegations.get(workflow_id)
