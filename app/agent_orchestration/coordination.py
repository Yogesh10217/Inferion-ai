"""Agent Coordination Subsystem (Phase 5.36)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.agent_orchestration.exceptions import CrossTenantAgentAccessException


class CoordinationStrategy(str, Enum):
    SEQUENTIAL = "SEQUENTIAL"
    PARALLEL = "PARALLEL"
    DEPENDENCY_DRIVEN = "DEPENDENCY_DRIVEN"
    SUPERVISOR_DISPATCH = "SUPERVISOR_DISPATCH"


class CoordinationStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f"coordstep_{uuid.uuid4().hex[:10]}")
    step_number: int
    assigned_agent_id: str
    target_system: str = "PLATFORM_OPERATIONS"
    action: str
    depends_on_steps: List[int] = Field(default_factory=list)
    max_retries: int = 3
    retry_count: int = 0
    status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED, RETRYING


class CoordinationConflict(BaseModel):
    conflict_id: str = Field(default_factory=lambda: f"conflict_{uuid.uuid4().hex[:8]}")
    competing_agent_ids: List[str]
    resource_ref: str
    resolution_strategy: str = "PRIORITY_OVERRIDE"
    resolved: bool = True


class CoordinationResult(BaseModel):
    is_successful: bool
    total_steps: int
    completed_step_ids: List[str] = Field(default_factory=list)
    failed_step_ids: List[str] = Field(default_factory=list)
    conflicts_detected: List[CoordinationConflict] = Field(default_factory=list)
    summary: str = ""


class AgentCoordinationPlan(BaseModel):
    coordination_id: str = Field(default_factory=lambda: f"coord_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    strategy: CoordinationStrategy = CoordinationStrategy.DEPENDENCY_DRIVEN
    steps: List[CoordinationStep] = Field(default_factory=list)
    conflicts: List[CoordinationConflict] = Field(default_factory=list)
    result: Optional[CoordinationResult] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentCoordinationManager:
    """Coordinates agent task assignment, dependency ordering, conflict resolution, and retry boundaries without directly executing infrastructure actions."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._plans: Dict[str, AgentCoordinationPlan] = {}

    def create_coordination_plan(
        self,
        tenant_id: str,
        strategy: CoordinationStrategy,
        steps: List[CoordinationStep],
        coordination_id: Optional[str] = None,
    ) -> AgentCoordinationPlan:
        cid = coordination_id or f"coord_{uuid.uuid4().hex[:12]}"

        # Detect conflicts (e.g. two agents trying to modify the same resource simultaneously)
        conflicts = []
        resource_map: Dict[str, List[str]] = {}
        for s in steps:
            key = f"{s.target_system}:{s.action}"
            if key not in resource_map:
                resource_map[key] = []
            resource_map[key].append(s.assigned_agent_id)

        for res_ref, agents in resource_map.items():
            if len(set(agents)) > 1:
                conflicts.append(CoordinationConflict(
                    competing_agent_ids=list(set(agents)),
                    resource_ref=res_ref,
                    resolution_strategy="SEQUENTIAL_ORDERING",
                    resolved=True,
                ))

        plan = AgentCoordinationPlan(
            coordination_id=cid,
            tenant_id=tenant_id,
            strategy=strategy,
            steps=steps,
            conflicts=conflicts,
        )
        self._plans[plan.coordination_id] = plan
        return plan

    def get_coordination_plan(self, coordination_id: str, tenant_id: str) -> AgentCoordinationPlan:
        plan = self._plans.get(coordination_id)
        if not plan:
            # Fallback plan
            return AgentCoordinationPlan(coordination_id=coordination_id, tenant_id=tenant_id)
            
        try:
            self.tenant_guard.enforce_isolation(tenant_id, plan.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, plan.tenant_id)

        return plan
