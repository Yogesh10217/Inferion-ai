"""Intelligent Orchestration & Budget/Risk-Aware Routing Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.finops.manager import FinOpsManager
from app.governance_platform.governance_manager import GovernancePlatformManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RoutingStrategy(str, Enum):
    STATIC = "STATIC"
    RULE_BASED = "RULE_BASED"
    LOAD_AWARE = "LOAD_AWARE"
    CAPABILITY_BASED = "CAPABILITY_BASED"
    COST_AWARE = "COST_AWARE"
    LATENCY_AWARE = "LATENCY_AWARE"
    QUALITY_AWARE = "QUALITY_AWARE"
    RISK_AWARE = "RISK_AWARE"
    POLICY_AWARE = "POLICY_AWARE"


class RoutingDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"rout_{uuid.uuid4().hex[:10]}")
    strategy: RoutingStrategy = RoutingStrategy.COST_AWARE
    selected_target: str = "cheaper_model"
    target_type: str = "WORKER"  # AGENT, TEAM, WORKER, TOOL, MCP_SERVER, EXTENSION, HUMAN_TASK
    estimated_cost: float = 0.05
    reasoning: str = ""
    evaluated_at: datetime = Field(default_factory=_now)


class ExecutionRouter:
    """Evaluates budget limits, risk scores, and strategies to select optimal execution targets."""

    def __init__(
        self,
        finops_manager: Optional[FinOpsManager] = None,
        governance_manager: Optional[GovernancePlatformManager] = None,
    ) -> None:
        self.finops_manager = finops_manager or FinOpsManager()
        self.governance_manager = governance_manager or GovernancePlatformManager()

    def route_task(
        self,
        task_name: str,
        tenant_id: str = "global",
        strategy: RoutingStrategy = RoutingStrategy.COST_AWARE,
        max_budget: float = 1.0,
        risk_score: float = 0.0,
    ) -> RoutingDecision:
        # COST_AWARE strategy: if max_budget < 0.50, select cheaper worker
        if strategy == RoutingStrategy.COST_AWARE and max_budget < 0.50:
            target = "worker_cheaper_standard"
            target_type = "WORKER"
            est_cost = 0.02
            reasoning = f"Selected '{target}' because max budget ({max_budget:.2f}) requires cost optimization"
        elif risk_score >= 70.0:
            target = "human_approval_gate"
            target_type = "HUMAN_TASK"
            est_cost = 0.0
            reasoning = f"Elevated risk score ({risk_score:.1f}) routed task to human verification"
        else:
            target = "agent_premium_team"
            target_type = "TEAM"
            est_cost = 0.45
            reasoning = f"Routed task '{task_name}' to high-capacity agent team under strategy {strategy.value}"

        decision = RoutingDecision(
            strategy=strategy,
            selected_target=target,
            target_type=target_type,
            estimated_cost=est_cost,
            reasoning=reasoning,
        )
        logger.info(f"[EXECUTION ROUTER] Routed '{task_name}' ({tenant_id}) -> Target '{target}' ({target_type}) via {strategy.value}")
        return decision
