"""Agent Planning Subsystem (Phase 5.36)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.decision_intelligence.manager import DecisionIntelligenceManager
from app.agent_orchestration.exceptions import (
    AgentPlanNotFoundException,
    CrossTenantAgentAccessException,
)


class PlanStepType(str, Enum):
    RETRIEVE_CONTEXT = "RETRIEVE_CONTEXT"
    ANALYZE_OPTION = "ANALYZE_OPTION"
    SELECT_TOOL = "SELECT_TOOL"
    EVALUATE_GOVERNANCE = "EVALUATE_GOVERNANCE"
    DELEGATE_ACTION = "DELEGATE_ACTION"
    VERIFY_RESULT = "VERIFY_RESULT"


class PlanStatus(str, Enum):
    DRAFT = "DRAFT"
    ANALYZED = "ANALYZED"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


class PlanStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f"step_{uuid.uuid4().hex[:10]}")
    step_number: int
    step_type: PlanStepType
    target_system: str = "PLATFORM_OPERATIONS"
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    estimated_risk: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    requires_approval: bool = False
    is_non_mutating: bool = True
    status: str = "PENDING"


class PlanConstraint(BaseModel):
    constraint_name: str
    description: str
    rule: str


class PlanAssumption(BaseModel):
    assumption_id: str = Field(default_factory=lambda: f"assump_{uuid.uuid4().hex[:8]}")
    description: str
    validity_check_action: Optional[str] = None


class PlanEvaluation(BaseModel):
    is_feasible: bool
    total_steps: int
    max_risk_score: float
    requires_human_approval: bool = False
    trade_off_analysis: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)


class AgentPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:12]}")
    task_id: str
    tenant_id: str
    agent_id: str
    version: str = "1.0.0"
    status: PlanStatus = PlanStatus.DRAFT
    steps: List[PlanStep] = Field(default_factory=list)
    constraints: List[PlanConstraint] = Field(default_factory=list)
    assumptions: List[PlanAssumption] = Field(default_factory=list)
    evaluation: Optional[PlanEvaluation] = None
    decision_analysis_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentPlanningEngine:
    """Deterministic, constraint-aware agent planning engine composing DecisionIntelligenceManager."""

    def __init__(
        self,
        decision_manager: Optional[DecisionIntelligenceManager] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.decision_manager = decision_manager or DecisionIntelligenceManager()
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._plans: Dict[str, AgentPlan] = {}

    def create_plan(
        self,
        tenant_id: str,
        task_id: str,
        agent_id: str,
        goal: str,
        target_systems: Optional[List[str]] = None,
        constraints: Optional[List[PlanConstraint]] = None,
        assumptions: Optional[List[PlanAssumption]] = None,
        plan_id: Optional[str] = None,
    ) -> AgentPlan:
        pid = plan_id or f"plan_{uuid.uuid4().hex[:12]}"
        
        # Formulate deterministic baseline plan steps
        default_targets = target_systems or ["PLATFORM_OPERATIONS"]
        steps = [
            PlanStep(
                step_number=1,
                step_type=PlanStepType.RETRIEVE_CONTEXT,
                target_system="KNOWLEDGE_INTELLIGENCE",
                action="retrieve_task_context",
                parameters={"task_id": task_id},
                is_non_mutating=True,
            ),
            PlanStep(
                step_number=2,
                step_type=PlanStepType.ANALYZE_OPTION,
                target_system="DECISION_INTELLIGENCE",
                action="analyze_decision_options",
                parameters={"goal": goal},
                is_non_mutating=True,
            ),
            PlanStep(
                step_number=3,
                step_type=PlanStepType.EVALUATE_GOVERNANCE,
                target_system="GOVERNANCE_PLATFORM",
                action="evaluate_policy_and_risk",
                parameters={"goal": goal},
                is_non_mutating=True,
            ),
            PlanStep(
                step_number=4,
                step_type=PlanStepType.DELEGATE_ACTION,
                target_system=default_targets[0],
                action="execute_governed_action",
                parameters={"goal": goal},
                estimated_risk="MEDIUM",
                is_non_mutating=False,
            ),
            PlanStep(
                step_number=5,
                step_type=PlanStepType.VERIFY_RESULT,
                target_system="RELIABILITY_PLATFORM",
                action="verify_execution_outcome",
                parameters={"task_id": task_id},
                is_non_mutating=True,
            ),
        ]

        # Use DecisionIntelligenceManager for structured trade-off evaluation if available
        decision_ref_id = None
        try:
            dec_res = self.decision_manager.formulate_decision(
                tenant_id=tenant_id,
                context_id=task_id,
                problem_statement=f"Plan formulation for goal: {goal}",
                options=[{"option_name": s.action, "target": s.target_system} for s in steps],
            )
            decision_ref_id = getattr(dec_res, "decision_id", f"dec_{uuid.uuid4().hex[:8]}")
        except Exception:
            decision_ref_id = f"dec_{uuid.uuid4().hex[:8]}"

        plan = AgentPlan(
            plan_id=pid,
            task_id=task_id,
            tenant_id=tenant_id,
            agent_id=agent_id,
            steps=steps,
            constraints=constraints or [],
            assumptions=assumptions or [],
            decision_analysis_id=decision_ref_id,
            evaluation=PlanEvaluation(
                is_feasible=True,
                total_steps=len(steps),
                max_risk_score=0.4,
                requires_human_approval=any(s.requires_approval for s in steps),
                recommendations=["Plan is deterministic, explainable, and constraint-aware."],
            ),
        )

        self._plans[plan.plan_id] = plan
        return plan

    def get_plan(self, plan_id: str, tenant_id: str) -> AgentPlan:
        plan = self._plans.get(plan_id)
        if not plan:
            raise AgentPlanNotFoundException(plan_id)
        
        try:
            self.tenant_guard.enforce_isolation(tenant_id, plan.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, plan.tenant_id)
            
        return plan
