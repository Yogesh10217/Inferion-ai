"""
Coordination & Action Planner Engine for Phase 5.51 Enterprise AI Unified Intelligence.

Plans multi-step cross-domain coordination plans, enforcing step dependencies,
approval gates, and execution parameters with tenant isolation.
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.unified_intelligence.domains import IntelligenceDomain
from app.unified_intelligence.exceptions import (
    CrossTenantUnifiedIntelligenceException,
    InvalidUnifiedIntelligenceInputException,
)
from app.unified_intelligence.recommendations import UnifiedRecommendation


class CoordinationStep:
    """
    Step in a cross-domain action coordination plan.
    """

    def __init__(
        self,
        step_id: str,
        target_domain: IntelligenceDomain,
        action_name: str,
        parameters: Dict[str, Any],
        depends_on_steps: List[str],
        requires_approval: bool,
        status: str = "PENDING"  # PENDING, IN_PROGRESS, COMPLETED, FAILED, WAITING_APPROVAL
    ):
        self.step_id = step_id
        self.target_domain = target_domain
        self.action_name = action_name
        self.parameters = parameters
        self.depends_on_steps = depends_on_steps
        self.requires_approval = requires_approval
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "target_domain": self.target_domain.value,
            "action_name": self.action_name,
            "parameters": self.parameters,
            "depends_on_steps": self.depends_on_steps,
            "requires_approval": self.requires_approval,
            "status": self.status
        }


class CoordinationPlan:
    """
    Multi-step execution plan for cross-domain action coordination.
    """

    def __init__(
        self,
        plan_id: str,
        tenant_id: str,
        recommendation_id: str,
        title: str,
        steps: List[CoordinationStep],
        overall_status: str = "DRAFT",  # DRAFT, APPROVED, IN_PROGRESS, EXECUTED, FAILED
        created_at: Optional[datetime] = None
    ):
        self.plan_id = plan_id
        self.tenant_id = tenant_id
        self.recommendation_id = recommendation_id
        self.title = title
        self.steps = steps
        self.overall_status = overall_status
        self.created_at = created_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "tenant_id": self.tenant_id,
            "recommendation_id": self.recommendation_id,
            "title": self.title,
            "steps": [s.to_dict() for s in self.steps],
            "overall_status": self.overall_status,
            "created_at": self.created_at.isoformat()
        }


class CoordinationPlannerEngine:
    """
    Builds structured coordination plans for execution across platform domain managers.
    """

    def __init__(self):
        pass

    def build_plan_for_recommendation(
        self,
        tenant_id: str,
        recommendation: UnifiedRecommendation
    ) -> CoordinationPlan:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")
        if recommendation.tenant_id != tenant_id:
            raise CrossTenantUnifiedIntelligenceException(
                f"Tenant mismatch in coordination plan building: expected {tenant_id}, got {recommendation.tenant_id}"
            )

        steps: List[CoordinationStep] = []
        plan_id = f"plan-{uuid.uuid4().hex[:12]}"

        # Create step for each domain
        prev_step_id = None
        for i, domain in enumerate(recommendation.target_domains):
            s_id = f"step-{i + 1}"
            step = CoordinationStep(
                step_id=s_id,
                target_domain=domain,
                action_name=f"Execute_{recommendation.action_type.lower()}_in_{domain.value.lower()}",
                parameters={
                    "recommendation_id": recommendation.recommendation_id,
                    "action_type": recommendation.action_type,
                    "priority": recommendation.priority
                },
                depends_on_steps=[prev_step_id] if prev_step_id else [],
                requires_approval=recommendation.requires_human_approval and i == 0
            )
            steps.append(step)
            prev_step_id = s_id

        return CoordinationPlan(
            plan_id=plan_id,
            tenant_id=tenant_id,
            recommendation_id=recommendation.recommendation_id,
            title=f"Coordination plan for: {recommendation.title}",
            steps=steps,
            overall_status="DRAFT"
        )
