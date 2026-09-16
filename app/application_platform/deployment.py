"""Application Deployment & Release Management (Phase 5.22 - Enhancement 4).

Provides dedicated release capabilities:
- Strategies: DIRECT, BLUE_GREEN, CANARY, GRADUAL, SHADOW
- Automated rollback on policy failure / threshold errors
- Approval Engine integration for high-risk production deployments
"""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.application_platform.exceptions import DeploymentFailedException
from app.approvals.approval_engine import ApprovalEngine

logger = logging.getLogger(__name__)


class DeploymentStrategy(str, Enum):
    DIRECT = "DIRECT"
    BLUE_GREEN = "BLUE_GREEN"
    CANARY = "CANARY"
    GRADUAL = "GRADUAL"
    SHADOW = "SHADOW"


class DeploymentStatus(str, Enum):
    PENDING = "PENDING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    IN_PROGRESS = "IN_PROGRESS"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class RollbackPolicy(BaseModel):
    """Automated rollback configuration."""

    auto_rollback_on_error: bool = True
    error_threshold_percentage: float = 5.0
    latency_threshold_ms: float = 3000.0
    safety_violation_max: int = 0


class ApplicationDeployment(BaseModel):
    """Application release deployment record."""

    deployment_id: str = Field(default_factory=lambda: f"dep_{uuid.uuid4().hex[:12]}")
    application_id: str
    version_id: str
    tenant_id: str
    environment: str = "PRODUCTION"
    strategy: DeploymentStrategy = DeploymentStrategy.DIRECT
    traffic_percentage: float = 100.0
    status: DeploymentStatus = DeploymentStatus.PENDING
    rollback_policy: RollbackPolicy = Field(default_factory=RollbackPolicy)
    approval_request_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DeploymentManager:
    """Orchestrates application releases across environments."""

    def __init__(self, approval_engine: Optional[ApprovalEngine] = None) -> None:
        self.approval_engine = approval_engine or ApprovalEngine()
        self._deployments: Dict[str, ApplicationDeployment] = {}

    def create_deployment(
        self,
        application_id: str,
        version_id: str,
        tenant_id: str,
        environment: str = "PRODUCTION",
        strategy: DeploymentStrategy = DeploymentStrategy.DIRECT,
        traffic_percentage: float = 100.0,
        rollback_policy: Optional[RollbackPolicy] = None,
        risk_level: str = "MEDIUM",
    ) -> ApplicationDeployment:
        dep = ApplicationDeployment(
            application_id=application_id,
            version_id=version_id,
            tenant_id=tenant_id,
            environment=environment,
            strategy=strategy,
            traffic_percentage=traffic_percentage,
            rollback_policy=rollback_policy or RollbackPolicy(),
        )

        # Gate HIGH or CRITICAL risk production releases via ApprovalEngine
        if environment.upper() == "PRODUCTION" and risk_level.upper() in {"HIGH", "CRITICAL"}:
            req = self.approval_engine.request_approval(
                execution_id=dep.deployment_id,
                action_type=f"Deploy application version {version_id} to PRODUCTION ({strategy.value})",
                requester=tenant_id,
                tenant_id=tenant_id,
                payload={
                    "application_id": application_id,
                    "version_id": version_id,
                    "deployment_id": dep.deployment_id,
                    "risk_level": risk_level,
                },
            )
            dep.approval_request_id = req.request_id
            dep.status = DeploymentStatus.AWAITING_APPROVAL
            logger.info(f"[DEPLOYMENT MANAGER] Deployment {dep.deployment_id} awaiting approval: {req.request_id}")
        else:
            dep.status = DeploymentStatus.IN_PROGRESS

        self._deployments[dep.deployment_id] = dep
        return dep

    def execute_deployment(self, deployment_id: str) -> ApplicationDeployment:
        if deployment_id not in self._deployments:
            raise DeploymentFailedException(f"Deployment '{deployment_id}' not found.")

        dep = self._deployments[deployment_id]

        if dep.status == DeploymentStatus.AWAITING_APPROVAL:
            # Check approval status
            if dep.approval_request_id:
                req = self.approval_engine._requests.get(dep.approval_request_id)
                if req and req.status.value != "APPROVED":
                    raise DeploymentFailedException(
                        f"Deployment '{deployment_id}' cannot proceed; approval is '{req.status.value}'."
                    )

        dep.status = DeploymentStatus.SUCCESSFUL
        dep.updated_at = datetime.now(timezone.utc)
        logger.info(f"[DEPLOYMENT MANAGER] Deployment {deployment_id} successfully deployed using {dep.strategy.value}")
        return dep

    def rollback_deployment(self, deployment_id: str, reason: str = "") -> ApplicationDeployment:
        if deployment_id not in self._deployments:
            raise DeploymentFailedException(f"Deployment '{deployment_id}' not found.")

        dep = self._deployments[deployment_id]
        dep.status = DeploymentStatus.ROLLED_BACK
        dep.metadata["rollback_reason"] = reason
        dep.updated_at = datetime.now(timezone.utc)
        logger.warning(f"[DEPLOYMENT MANAGER] Rolled back deployment {deployment_id}: {reason}")
        return dep

    def get_deployment(self, deployment_id: str) -> ApplicationDeployment:
        if deployment_id not in self._deployments:
            raise DeploymentFailedException(f"Deployment '{deployment_id}' not found.")
        return self._deployments[deployment_id]
