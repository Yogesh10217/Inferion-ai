"""Controlled Recovery Subsystem (Phase 5.36)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.agent_orchestration.delegation import AgentDelegationManager
from app.agent_orchestration.exceptions import CrossTenantAgentAccessException
from app.platform_contracts.delegation import DelegationTarget
from app.platform_contracts.tenant import TenantAccessGuard


class RecoveryStrategy(str, Enum):
    RETRY = "RETRY"
    REPLAN = "REPLAN"
    FALLBACK_AGENT = "FALLBACK_AGENT"
    ESCALATE_HUMAN = "ESCALATE_HUMAN"
    ROLLBACK_REQUEST = "ROLLBACK_REQUEST"
    STOP = "STOP"


class RecoveryStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"


class RecoveryAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"recact_{uuid.uuid4().hex[:10]}")
    strategy: RecoveryStrategy
    target_agent_id: Optional[str] = None
    delegation_id: Optional[str] = None
    description: str = ""


class AgentRecoveryPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"recplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    execution_id: str
    task_id: str
    strategy: RecoveryStrategy = RecoveryStrategy.RETRY
    actions: List[RecoveryAction] = Field(default_factory=list)
    status: RecoveryStatus = RecoveryStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentRecoveryManager:
    """Formulates and executes recovery plans, routing rollbacks via delegation requests."""

    def __init__(
        self,
        delegation_manager: Optional[AgentDelegationManager] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.delegation_manager = delegation_manager or AgentDelegationManager()
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._plans: Dict[str, AgentRecoveryPlan] = {}

    def formulate_recovery(
        self,
        tenant_id: str,
        execution_id: str,
        task_id: str,
        failure_reason: str,
        is_unsafe_for_auto_recovery: bool = False,
        fallback_agent_id: Optional[str] = None,
    ) -> AgentRecoveryPlan:
        actions = []

        if is_unsafe_for_auto_recovery:
            strategy = RecoveryStrategy.ESCALATE_HUMAN
            actions.append(
                RecoveryAction(
                    strategy=RecoveryStrategy.ESCALATE_HUMAN,
                    description=f"Automated recovery is unsafe for failure '{failure_reason}'. Escalating to human oversight.",
                )
            )
        elif fallback_agent_id:
            strategy = RecoveryStrategy.FALLBACK_AGENT
            actions.append(
                RecoveryAction(
                    strategy=RecoveryStrategy.FALLBACK_AGENT,
                    target_agent_id=fallback_agent_id,
                    description=f"Routing task execution to fallback agent '{fallback_agent_id}'.",
                )
            )
        else:
            strategy = RecoveryStrategy.ROLLBACK_REQUEST
            # Emit governed delegation request to PLATFORM_OPERATIONS for rollback
            del_req = self.delegation_manager.create_delegation_request(
                tenant_id=tenant_id,
                target=DelegationTarget.PLATFORM_OPERATIONS,
                action="rollback_execution_state",
                payload={"execution_id": execution_id, "reason": failure_reason},
            )
            actions.append(
                RecoveryAction(
                    strategy=RecoveryStrategy.ROLLBACK_REQUEST,
                    delegation_id=del_req.delegation_id,
                    description=f"Delegated rollback request created ({del_req.delegation_id}).",
                )
            )

        plan = AgentRecoveryPlan(
            tenant_id=tenant_id,
            execution_id=execution_id,
            task_id=task_id,
            strategy=strategy,
            actions=actions,
            status=(
                RecoveryStatus.IN_PROGRESS if strategy != RecoveryStrategy.ESCALATE_HUMAN else RecoveryStatus.ESCALATED
            ),
        )
        self._plans[plan.plan_id] = plan
        return plan

    def get_recovery_plan(self, plan_id: str, tenant_id: str) -> AgentRecoveryPlan:
        plan = self._plans.get(plan_id)
        if not plan:
            return AgentRecoveryPlan(plan_id=plan_id, tenant_id=tenant_id, execution_id="unknown", task_id="unknown")

        try:
            self.tenant_guard.enforce_isolation(tenant_id, plan.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, plan.tenant_id)

        return plan
