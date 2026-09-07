"""
Autonomous Workflow Planning Subsystem.
Constructs multi-step execution plans incorporating risk, impact, policy, trust, confidence, cost, and reversibility.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.autonomous_assurance.workflow_steps import WorkflowStep, WorkflowStepType


class AutonomousPlanConstraint(BaseModel):
    constraint_type: str = "POLICY"
    rule_id: str
    description: str
    severity: str = "HARD"


class AutonomousPlanStep(BaseModel):
    step_id: str = Field(default_factory=lambda: f"pstep_{uuid.uuid4().hex[:12]}")
    sequence: int
    step_name: str
    action_type: str = "DELEGATE_ACTION"
    target_system: str = "OPERATIONS"
    estimated_duration_seconds: int = 30
    reversibility: str = "REVERSIBLE"
    requires_approval: bool = False
    parameters: Dict[str, Any] = Field(default_factory=dict)


class AutonomousPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    version: str = "1.0.0"
    plan_steps: List[AutonomousPlanStep] = Field(default_factory=list)
    constraints: List[AutonomousPlanConstraint] = Field(default_factory=list)
    estimated_cost: float = 0.0
    risk_score: float = 20.0
    trust_score: float = 90.0
    confidence_score: float = 0.95
    requires_approval: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def ordered_steps(self) -> List[AutonomousPlanStep]:
        return sorted(self.plan_steps, key=lambda s: s.sequence)


class AutonomousPlanner:
    """Constructs structured autonomous workflow plans."""

    def __init__(self) -> None:
        self._plans: Dict[str, AutonomousPlan] = {}

    def create_plan(
        self,
        workflow_id: str,
        tenant_id: str,
        steps: Optional[List[AutonomousPlanStep]] = None,
        risk_score: float = 20.0,
        trust_score: float = 90.0,
    ) -> AutonomousPlan:
        plan_steps = steps or [
            AutonomousPlanStep(
                sequence=1,
                step_name="Analyze Cross-Domain Signals",
                action_type="ANALYZE",
                target_system="UNIFIED_INTELLIGENCE",
                requires_approval=False,
            ),
            AutonomousPlanStep(
                sequence=2,
                step_name="Dispatch Remediation Delegation",
                action_type="DELEGATE",
                target_system="OPERATIONS",
                requires_approval=(risk_score >= 50.0),
            ),
            AutonomousPlanStep(
                sequence=3,
                step_name="Verify Operational Health Post-Execution",
                action_type="VERIFY",
                target_system="OPERATIONS_ASSURANCE",
                requires_approval=False,
            ),
        ]

        req_appr = (risk_score >= 50.0) or (trust_score < 70.0) or any(s.requires_approval for s in plan_steps)

        plan = AutonomousPlan(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            plan_steps=plan_steps,
            risk_score=risk_score,
            trust_score=trust_score,
            requires_approval=req_appr,
        )
        self._plans[workflow_id] = plan
        return plan

    def generate_plan(self, workflow_id: str, tenant_id: str) -> AutonomousPlan:
        wf_steps = []
        if hasattr(self, "manager") and self.manager:
            wf_steps = self.manager.get_steps(workflow_id)

        if wf_steps:
            plan_steps = [
                AutonomousPlanStep(
                    step_id=s.step_id,
                    sequence=idx + 1,
                    step_name=s.step_name,
                    action_type=s.action_name,
                    target_system=s.target_system,
                    requires_approval=("RESTART" in s.action_name or "DISABLE" in s.action_name),
                )
                for idx, s in enumerate(wf_steps)
            ]
            return self.create_plan(workflow_id, tenant_id, steps=plan_steps)

        return self.create_plan(workflow_id, tenant_id)

    def get_plan(self, workflow_id: str) -> Optional[AutonomousPlan]:
        return self._plans.get(workflow_id)
