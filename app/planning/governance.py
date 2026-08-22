"""
Governance Engine for Autonomous Planning & Execution
"""

import logging
from typing import Dict, Any, List, Optional
from app.planning.execution_plan import ExecutionPlan
from app.planning.exceptions import ResourcePlanningError

logger = logging.getLogger(__name__)


class PlanningGovernanceEngine:
    """Enforces multi-tenant boundaries, budget caps, risk thresholds, and approval rules."""

    @staticmethod
    def validate_plan_execution(
        plan: ExecutionPlan,
        tenant_id: str,
        workspace_budget_dollars: float = 50.0,
        user_scopes: Optional[List[str]] = None,
        confidence_threshold: float = 0.70,
    ) -> None:
        user_scopes = user_scopes or ["plans:execute"]

        # 1. Multi-Tenant Isolation
        if plan.tenant_id not in (tenant_id, "global", "default_tenant"):
            raise ResourcePlanningError(f"Tenant isolation violation: plan tenant '{plan.tenant_id}' != request tenant '{tenant_id}'")

        # 2. RBAC Scope Validation
        if "plans:execute" not in user_scopes and "admin" not in user_scopes:
            raise ResourcePlanningError(f"User scopes {user_scopes} missing required scope 'plans:execute'")

        # 3. Budget Limits
        if plan.estimated_cost > workspace_budget_dollars:
            raise ResourcePlanningError(f"Workspace budget exceeded: plan cost ${plan.estimated_cost:.4f} > workspace budget ${workspace_budget_dollars:.4f}")

        # 4. Confidence Threshold
        if plan.confidence_score < confidence_threshold:
            raise ResourcePlanningError(f"Plan confidence score {plan.confidence_score:.2f} below threshold {confidence_threshold:.2f}")

        logger.info(f"[PLANNING GOVERNANCE] Approved plan '{plan.plan_id}' for execution")
