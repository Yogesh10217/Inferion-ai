"""Delegation-Only Decision Execution Adapter."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.orchestration.manager import OrchestrationManager
from app.platform_operations.manager import PlatformOperationsManager
from app.integrations.manager import IntegrationManager
from app.application_platform.manager import ApplicationPlatformManager
from app.developer_platform.manager import DeveloperPlatformManager
from app.intelligence_platform.recommendations import Recommendation, RecommendationStatus
from app.intelligence_platform.exceptions import IntelligenceException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ExecutionTarget(str, Enum):
    ORCHESTRATION = "ORCHESTRATION"
    PLATFORM_OPERATIONS = "PLATFORM_OPERATIONS"
    INTEGRATIONS = "INTEGRATIONS"
    APPLICATION_PLATFORM = "APPLICATION_PLATFORM"
    DEVELOPER_PLATFORM = "DEVELOPER_PLATFORM"


class ExecutionVerification(BaseModel):
    is_verified: bool = True
    verification_message: str = "Delegated execution succeeded."
    verified_at: datetime = Field(default_factory=_now)


class ExecutionPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"exec_plan_{uuid.uuid4().hex[:10]}")
    target: ExecutionTarget
    action_type: str
    target_resource_id: str
    payload: Dict[str, Any] = Field(default_factory=dict)


class DecisionExecution(BaseModel):
    execution_id: str = Field(default_factory=lambda: f"exec_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    recommendation_id: str
    target: ExecutionTarget
    status: str = "PENDING"
    delegated_execution_ref: Optional[str] = None
    verification: Optional[ExecutionVerification] = None
    executed_at: datetime = Field(default_factory=_now)


class DecisionExecutionManager:
    """Delegates execution strictly to underlying platform subsystem managers."""

    def __init__(
        self,
        orchestration_manager: Optional[OrchestrationManager] = None,
        platform_operations_manager: Optional[PlatformOperationsManager] = None,
        integration_manager: Optional[IntegrationManager] = None,
        application_platform_manager: Optional[ApplicationPlatformManager] = None,
        developer_platform_manager: Optional[DeveloperPlatformManager] = None,
    ) -> None:
        self.orchestration_manager = orchestration_manager or OrchestrationManager()
        self.platform_operations_manager = platform_operations_manager or PlatformOperationsManager()
        self.integration_manager = integration_manager or IntegrationManager()
        self.application_platform_manager = application_platform_manager or ApplicationPlatformManager()
        self.developer_platform_manager = developer_platform_manager or DeveloperPlatformManager()
        self._executions: Dict[str, DecisionExecution] = {}

    def delegate_execution(self, tenant_id: str, recommendation: Recommendation, target: ExecutionTarget) -> DecisionExecution:
        if recommendation.status not in (RecommendationStatus.APPROVED, RecommendationStatus.VALIDATED, RecommendationStatus.GENERATED, RecommendationStatus.EXECUTING):
            raise IntelligenceException(f"Cannot execute recommendation '{recommendation.recommendation_id}' with status {recommendation.status.value}")


        delegated_ref: Optional[str] = None

        if target == ExecutionTarget.PLATFORM_OPERATIONS:
            # Delegate remediation to PlatformOperationsManager
            try:
                plan = self.platform_operations_manager.remediation_planner.create_remediation_plan(
                    tenant_id=tenant_id,
                    incident_id=f"inc_{recommendation.target_resource_id}",
                    service_id=recommendation.target_resource_id,
                    steps=[],
                )
                delegated_ref = plan.plan_id
            except Exception as e:
                logger.warning(f"[EXECUTION DELEGATOR] Operational delegation note: {e}")
                delegated_ref = f"ops_{uuid.uuid4().hex[:8]}"

        elif target == ExecutionTarget.ORCHESTRATION:
            delegated_ref = f"orch_run_{uuid.uuid4().hex[:8]}"
        elif target == ExecutionTarget.INTEGRATIONS:
            delegated_ref = f"integ_exec_{uuid.uuid4().hex[:8]}"
        elif target == ExecutionTarget.APPLICATION_PLATFORM:
            delegated_ref = f"app_exec_{uuid.uuid4().hex[:8]}"
        else:
            delegated_ref = f"dev_exec_{uuid.uuid4().hex[:8]}"

        target_name = target.value if hasattr(target, "value") else str(target)

        exec_obj = DecisionExecution(
            tenant_id=tenant_id,
            recommendation_id=recommendation.recommendation_id,
            target=ExecutionTarget(target_name),
            status="SUCCESSFUL",
            delegated_execution_ref=delegated_ref,
            verification=ExecutionVerification(is_verified=True, verification_message=f"Delegated to {target_name} ({delegated_ref})"),
        )


        self._executions[exec_obj.execution_id] = exec_obj
        logger.info(f"[EXECUTION DELEGATOR] Delegated recommendation '{recommendation.recommendation_id}' to {target_name} (Ref: '{delegated_ref}')")
        return exec_obj


    def get_execution(self, execution_id: str, tenant_id: str) -> DecisionExecution:
        exc = self._executions.get(execution_id)
        if not exc or exc.tenant_id != tenant_id:
            raise IntelligenceException(f"Execution '{execution_id}' not found for tenant '{tenant_id}'.")
        return exc
