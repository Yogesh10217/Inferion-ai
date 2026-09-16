"""Agent Runtime Governance Subsystem (Phase 5.36)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.agent_orchestration.exceptions import (
    AgentBudgetExceededException,
    AgentRuntimeLimitExceededException,
    CrossTenantAgentAccessException,
)
from app.platform_contracts.tenant import TenantAccessGuard


class RuntimeStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    EXCEEDED_LIMIT = "EXCEEDED_LIMIT"
    LOOP_DETECTED = "LOOP_DETECTED"
    TERMINATED = "TERMINATED"


class RuntimeLimit(BaseModel):
    max_duration_sec: int = 300
    max_invocations: int = 50
    max_recursion_depth: int = 5
    max_cost_dollars: float = 100.0


class RuntimeBudget(BaseModel):
    allocated_cost: float = 100.0
    consumed_cost: float = 0.0
    allocated_time_sec: int = 300
    consumed_time_sec: int = 0


class RuntimeViolation(BaseModel):
    violation_type: str
    dimension: str
    current_value: Any
    limit_value: Any
    message: str


class RuntimeCheckpoint(BaseModel):
    checkpoint_id: str = Field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:8]}")
    step_number: int
    state_hash: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentRuntimeSession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"rtsess_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    agent_id: str
    execution_id: str
    status: RuntimeStatus = RuntimeStatus.ACTIVE
    step_count: int = 0
    recursion_depth: int = 0
    consumed_cost: float = 0.0
    duration_sec: int = 0
    tool_invocations: int = 0
    limit: RuntimeLimit = Field(default_factory=RuntimeLimit)
    budget: RuntimeBudget = Field(default_factory=RuntimeBudget)
    violations: List[RuntimeViolation] = Field(default_factory=list)
    recent_action_hashes: List[str] = Field(default_factory=list)
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentRuntimeManager:
    """Monitors agent runtime metrics and enforces safeguards against infinite recursion and budget overruns."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._sessions: Dict[str, AgentRuntimeSession] = {}

    def create_session(
        self,
        tenant_id: str,
        agent_id: str,
        execution_id: str,
        limit: Optional[RuntimeLimit] = None,
        budget: Optional[RuntimeBudget] = None,
    ) -> AgentRuntimeSession:
        sess = AgentRuntimeSession(
            tenant_id=tenant_id,
            agent_id=agent_id,
            execution_id=execution_id,
            limit=limit or RuntimeLimit(),
            budget=budget or RuntimeBudget(),
        )
        self._sessions[sess.session_id] = sess
        return sess

    def get_session(self, session_id: str, tenant_id: str) -> AgentRuntimeSession:
        sess = self._sessions.get(session_id)
        if not sess:
            # Fallback
            return AgentRuntimeSession(session_id=session_id, tenant_id=tenant_id, agent_id="unknown", execution_id="unknown")

        try:
            self.tenant_guard.enforce_isolation(tenant_id, sess.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, sess.tenant_id)

        return sess

    def record_step(
        self,
        session_id: str,
        tenant_id: str,
        action_name: str,
        cost: float = 0.0,
        is_tool_call: bool = False,
    ) -> AgentRuntimeSession:
        sess = self.get_session(session_id, tenant_id)

        if sess.status in (RuntimeStatus.TERMINATED, RuntimeStatus.EXCEEDED_LIMIT, RuntimeStatus.LOOP_DETECTED):
            raise AgentRuntimeLimitExceededException(f"Runtime session is in '{sess.status.value}' state.")

        sess.step_count += 1
        sess.consumed_cost += cost
        sess.budget.consumed_cost += cost
        if is_tool_call:
            sess.tool_invocations += 1

        # Calculate duration
        now = datetime.now(timezone.utc)
        sess.duration_sec = int((now - sess.start_time).total_seconds())

        # Loop detection (identical repeated action string)
        action_hash = f"{action_name}_{sess.step_count}"
        sess.recent_action_hashes.append(action_name)
        if len(sess.recent_action_hashes) > 10:
            sess.recent_action_hashes.pop(0)

        # Check loop condition: if last 4 actions are identical
        if len(sess.recent_action_hashes) >= 4 and len(set(sess.recent_action_hashes[-4:])) == 1:
            sess.status = RuntimeStatus.LOOP_DETECTED
            v = RuntimeViolation(
                violation_type="RECURSION_LOOP",
                dimension="recursion_depth",
                current_value=sess.recent_action_hashes[-4:],
                limit_value=3,
                message=f"Infinite loop detected: Action '{action_name}' repeated 4 times consecutively."
            )
            sess.violations.append(v)
            raise AgentRuntimeLimitExceededException(v.message)

        # Check step count limit
        if sess.step_count > sess.limit.max_invocations:
            sess.status = RuntimeStatus.EXCEEDED_LIMIT
            v = RuntimeViolation(
                violation_type="MAX_STEPS_EXCEEDED",
                dimension="max_invocations",
                current_value=sess.step_count,
                limit_value=sess.limit.max_invocations,
                message=f"Maximum step count ({sess.limit.max_invocations}) exceeded."
            )
            sess.violations.append(v)
            raise AgentRuntimeLimitExceededException(v.message)

        # Check cost budget limit
        if sess.consumed_cost > sess.limit.max_cost_dollars:
            sess.status = RuntimeStatus.EXCEEDED_LIMIT
            v = RuntimeViolation(
                violation_type="MAX_COST_EXCEEDED",
                dimension="max_cost_dollars",
                current_value=sess.consumed_cost,
                limit_value=sess.limit.max_cost_dollars,
                message=f"Financial cost budget ${sess.limit.max_cost_dollars:.2f} exceeded."
            )
            sess.violations.append(v)
            raise AgentBudgetExceededException(v.message)

        return sess
