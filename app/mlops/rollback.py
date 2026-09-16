"""Automated Rollback & Recovery Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field

from app.mlops.deployment import DeploymentManager
from app.mlops.registry import AIAssetRegistry

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class RollbackPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"rb_plan_{uuid.uuid4().hex[:10]}")
    deployment_id: str
    target_version_number: str
    reason: str = "Automated rollback triggered by guardrail failure"
    created_at: datetime = Field(default_factory=_now)


class RollbackResult(BaseModel):
    result_id: str = Field(default_factory=lambda: f"rb_res_{uuid.uuid4().hex[:10]}")
    plan_id: str
    deployment_id: str
    restored_version_number: str
    success: bool = True
    executed_at: datetime = Field(default_factory=_now)


class RollbackManager:
    """Manages deployment, model, prompt, agent, workflow, and full release rollback plans."""

    def __init__(self, deployment_manager: Optional[DeploymentManager] = None, registry: Optional[AIAssetRegistry] = None) -> None:
        self.deployment_manager = deployment_manager or DeploymentManager()
        self.registry = registry or AIAssetRegistry()
        self._history: List[RollbackResult] = []

    def create_rollback_plan(self, deployment_id: str, target_version_number: str, reason: str = "") -> RollbackPlan:
        plan = RollbackPlan(deployment_id=deployment_id, target_version_number=target_version_number, reason=reason)
        logger.info(f"[ROLLBACK MANAGER] Created rollback plan for deployment '{deployment_id}' -> v{target_version_number}")
        return plan

    def execute_rollback(self, plan: RollbackPlan) -> RollbackResult:
        dep = self.deployment_manager.get_deployment(plan.deployment_id)
        self.deployment_manager.rollback(plan.deployment_id, plan.target_version_number)

        result = RollbackResult(
            plan_id=plan.plan_id,
            deployment_id=plan.deployment_id,
            restored_version_number=plan.target_version_number,
            success=True,
        )
        self._history.append(result)
        logger.info(f"[ROLLBACK MANAGER] Successfully executed rollback for deployment '{plan.deployment_id}' to v{plan.target_version_number}")
        return result
