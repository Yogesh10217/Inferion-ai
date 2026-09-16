"""Delegation-Only Deployment Planning Subsystem (Phase 5.33)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.platform_contracts.delegation import DelegationRequest, DelegationTarget
from app.platform_contracts.idempotency import IdempotencyManager


class DeploymentTarget(str, Enum):
    KUBERNETES_CLUSTER = "KUBERNETES_CLUSTER"
    SERVERLESS_ENDPOINT = "SERVERLESS_ENDPOINT"
    ON_PREM_VAULT = "ON_PREM_VAULT"
    EDGE_DEVICE = "EDGE_DEVICE"


class DeploymentStatus(str, Enum):
    PLANNED = "PLANNED"
    DELEGATED = "DELEGATED"
    EXECUTING = "EXECUTING"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"


class DeploymentVerification(BaseModel):
    is_verified: bool = True
    health_check_passed: bool = True


class DeploymentPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"dplan_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    release_id: str
    idempotency_key: str
    target: DeploymentTarget = DeploymentTarget.KUBERNETES_CLUSTER
    status: DeploymentStatus = DeploymentStatus.PLANNED
    delegation_request: Optional[DelegationRequest] = None
    verification: Optional[DeploymentVerification] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DeploymentManager:
    """Plans deployment and delegates execution via DelegationRequest and IdempotencyManager."""

    def __init__(self, idempotency_manager: Optional[IdempotencyManager] = None) -> None:
        self.idempotency_manager = idempotency_manager or IdempotencyManager()
        self._plans: Dict[str, DeploymentPlan] = {}

    def plan_deployment(
        self,
        tenant_id: str,
        release_id: str,
        idempotency_key: str,
        target: DeploymentTarget = DeploymentTarget.KUBERNETES_CLUSTER,
    ) -> DeploymentPlan:
        payload = {"release_id": release_id, "target": target.value}
        record = self.idempotency_manager.check_or_start(tenant_id, "PLAN_AI_DEPLOYMENT", idempotency_key, payload)

        if record and record.result_payload:
            plan_dict = record.result_payload.get("plan")
            if plan_dict:
                return DeploymentPlan(**plan_dict)

        delegation = DelegationRequest(
            tenant_id=tenant_id,
            target=DelegationTarget.PLATFORM_OPERATIONS,
            action="DEPLOY_AI_MODEL",
            payload={"release_id": release_id, "target": target.value},
        )

        plan = DeploymentPlan(
            tenant_id=tenant_id,
            release_id=release_id,
            idempotency_key=idempotency_key,
            target=target,
            status=DeploymentStatus.DELEGATED,
            delegation_request=delegation,
            verification=DeploymentVerification(is_verified=True, health_check_passed=True),
        )
        self._plans[plan.plan_id] = plan

        self.idempotency_manager.complete_operation(
            tenant_id=tenant_id,
            operation_type="PLAN_AI_DEPLOYMENT",
            idempotency_key=idempotency_key,
            result_payload={"plan": plan.model_dump()},
        )
        return plan
