"""Agent Cost Attribution Subsystem (Phase 5.36)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.finops.manager import FinOpsManager
from app.platform_contracts.tenant import TenantAccessGuard
from app.agent_orchestration.exceptions import CrossTenantAgentAccessException


class AgentCostDimension(str, Enum):
    MODEL_USAGE = "MODEL_USAGE"
    TOOL_USAGE = "TOOL_USAGE"
    EXECUTION_DURATION = "EXECUTION_DURATION"
    DELEGATED_OPERATIONS = "DELEGATED_OPERATIONS"


class AgentCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"costevt_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    agent_id: str
    task_id: str
    dimension: AgentCostDimension = AgentCostDimension.MODEL_USAGE
    cost_dollars: float = 0.0
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentBillingTracker:
    """Tracks agent cost events across dimensions and delegates to FinOpsManager."""

    def __init__(
        self,
        finops_manager: Optional[FinOpsManager] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.finops_manager = finops_manager or FinOpsManager()
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._events: List[AgentCostEvent] = []

    def record_cost(
        self,
        tenant_id: str,
        agent_id: str,
        task_id: str,
        dimension: AgentCostDimension,
        cost_dollars: float,
        details: Optional[Dict[str, Any]] = None,
    ) -> AgentCostEvent:
        event = AgentCostEvent(
            tenant_id=tenant_id,
            agent_id=agent_id,
            task_id=task_id,
            dimension=dimension,
            cost_dollars=cost_dollars,
            details=details or {},
        )

        # Delegate cost event to FinOpsManager if supported
        try:
            self.finops_manager.record_usage_cost(
                tenant_id=tenant_id,
                resource_id=f"agent_{agent_id}",
                cost_amount=cost_dollars,
                category=dimension.value,
            )
        except Exception:
            pass

        self._events.append(event)
        return event

    def get_agent_total_cost(self, agent_id: str, tenant_id: str) -> float:
        total = 0.0
        for ev in self._events:
            if ev.agent_id == agent_id and (ev.tenant_id == tenant_id or tenant_id == "global"):
                total += ev.cost_dollars
        return total
