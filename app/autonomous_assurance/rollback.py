"""
Workflow Rollback Planning Subsystem.
Constructs safe rollback plans supporting FULL, PARTIAL, SAFE, MANUAL, and DELEGATED strategies.
Does NOT directly execute infrastructure rollback actions.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RollbackStrategy(str, Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    SAFE = "SAFE"
    MANUAL = "MANUAL"
    DELEGATED = "DELEGATED"


class RollbackPlan(BaseModel):
    rollback_id: str = Field(default_factory=lambda: f"rb_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    strategy: RollbackStrategy = RollbackStrategy.SAFE
    rollback_actions: List[Any] = Field(default_factory=list)
    requires_approval: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RollbackPlanner:
    """Plans delegated rollback operations."""

    def __init__(self) -> None:
        self._plans: Dict[str, RollbackPlan] = {}

    def plan_rollback(
        self, workflow_id: str, tenant_id: str, strategy: RollbackStrategy = RollbackStrategy.SAFE
    ) -> RollbackPlan:
        plan = RollbackPlan(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            strategy=strategy,
            rollback_actions=[
                {"action": "DELEGATE_ROLLBACK_DEPLOYMENT", "target": "OPERATIONS"},
                {"action": "VERIFY_ROLLBACK_HEALTH", "target": "OPERATIONS_ASSURANCE"},
            ],
            requires_approval=(strategy in (RollbackStrategy.FULL, RollbackStrategy.MANUAL)),
        )
        self._plans[workflow_id] = plan
        return plan

    def create_rollback_plan(
        self,
        workflow_id: str,
        tenant_id: str,
        executed_actions: Optional[List[str]] = None,
        strategy: RollbackStrategy = RollbackStrategy.SAFE,
    ) -> RollbackPlan:
        action_map = {
            "DISABLE_ROUTE": "ENABLE_ROUTE",
            "DRAIN_TRAFFIC": "RESTORE_TRAFFIC",
            "RESTART_SERVICE": "RESTORE_SERVICE",
        }
        reversed_actions = [action_map.get(act, f"REVERSE_{act}") for act in reversed(executed_actions or [])]
        plan = RollbackPlan(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            strategy=strategy,
            rollback_actions=reversed_actions or ["RESTORE_STATE"],
        )
        self._plans[workflow_id] = plan
        return plan

    def get_rollback_plan(self, workflow_id: str) -> Optional[RollbackPlan]:
        return self._plans.get(workflow_id)
