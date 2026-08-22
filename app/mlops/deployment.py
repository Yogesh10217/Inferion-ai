"""Deployment Management & Production Lifecycle Subsystem."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.mlops.registry import AIAssetRegistry, AIAssetStatus
from app.mlops.exceptions import DeploymentNotFoundException, GovernanceViolationException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DeploymentEnvironment(str, Enum):
    DEVELOPMENT = "DEVELOPMENT"
    TESTING = "TESTING"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


class DeploymentStatus(str, Enum):
    PENDING = "PENDING"
    VALIDATING = "VALIDATING"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    DEPLOYING = "DEPLOYING"
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    FAILED = "FAILED"
    ROLLING_BACK = "ROLLING_BACK"
    ROLLED_BACK = "ROLLED_BACK"
    STOPPED = "STOPPED"


class Deployment(BaseModel):
    deployment_id: str = Field(default_factory=lambda: f"dep_{uuid.uuid4().hex[:10]}")
    name: str
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None

    asset_id: str
    version_number: str
    environment: DeploymentEnvironment = DeploymentEnvironment.DEVELOPMENT
    status: DeploymentStatus = DeploymentStatus.PENDING

    active_traffic_percentage: float = 100.0
    previous_version_number: Optional[str] = None
    approval_request_id: Optional[str] = None

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class DeploymentManager:
    """Manages multi-environment deployments, approval gating, and production health state."""

    def __init__(self, registry: Optional[AIAssetRegistry] = None) -> None:
        self.registry = registry or AIAssetRegistry()
        self._deployments: Dict[str, Deployment] = {}

    def create_deployment(
        self,
        name: str,
        asset_id: str,
        version_number: str,
        environment: DeploymentEnvironment = DeploymentEnvironment.DEVELOPMENT,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Deployment:
        ver = self.registry.get_version(asset_id, version_number)

        dep = Deployment(
            name=name,
            asset_id=asset_id,
            version_number=version_number,
            environment=environment,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            status=DeploymentStatus.PENDING,
        )

        if environment == DeploymentEnvironment.PRODUCTION and not ver.is_immutable:
            # Require validation & approval for production!
            dep.status = DeploymentStatus.APPROVAL_REQUIRED
            dep.approval_request_id = f"appr_req_{uuid.uuid4().hex[:8]}"
            logger.info(f"[DEPLOYMENT MANAGER] Production deployment '{dep.deployment_id}' requires approval")

        self._deployments[dep.deployment_id] = dep
        return dep

    def deploy(self, deployment_id: str) -> Deployment:
        dep = self.get_deployment(deployment_id)

        if dep.environment == DeploymentEnvironment.PRODUCTION and dep.status == DeploymentStatus.APPROVAL_REQUIRED:
            raise GovernanceViolationException(f"Production deployment '{deployment_id}' requires explicit approval before deploy")

        dep.status = DeploymentStatus.ACTIVE
        dep.updated_at = _now()

        # Update asset status in registry
        self.registry.promote_version(dep.asset_id, dep.version_number, AIAssetStatus.PRODUCTION if dep.environment == DeploymentEnvironment.PRODUCTION else AIAssetStatus.STAGED)

        logger.info(f"[DEPLOYMENT MANAGER] Deployed '{dep.name}' to '{dep.environment.value}' (Status: ACTIVE)")
        return dep

    def approve_deployment(self, deployment_id: str) -> Deployment:
        dep = self.get_deployment(deployment_id)
        dep.status = DeploymentStatus.VALIDATING
        dep.approval_request_id = None
        dep.updated_at = _now()
        logger.info(f"[DEPLOYMENT MANAGER] Approved deployment '{deployment_id}'")
        return dep

    def rollback(self, deployment_id: str, previous_version_number: str) -> Deployment:
        dep = self.get_deployment(deployment_id)
        dep.previous_version_number = dep.version_number
        dep.version_number = previous_version_number
        dep.status = DeploymentStatus.ROLLED_BACK
        dep.updated_at = _now()

        self.registry.rollback_version(dep.asset_id, previous_version_number)
        logger.info(f"[DEPLOYMENT MANAGER] Rolled back deployment '{deployment_id}' to version '{previous_version_number}'")
        return dep

    def get_deployment(self, deployment_id: str) -> Deployment:
        dep = self._deployments.get(deployment_id)
        if not dep:
            raise DeploymentNotFoundException(deployment_id)
        return dep

    def list_deployments(self, tenant_id: Optional[str] = None, environment: Optional[DeploymentEnvironment] = None) -> List[Deployment]:
        res = list(self._deployments.values())
        if tenant_id:
            res = [d for d in res if d.tenant_id == tenant_id]
        if environment:
            res = [d for d in res if d.environment == environment]
        return res
