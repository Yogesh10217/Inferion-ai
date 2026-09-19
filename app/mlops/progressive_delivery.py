"""Progressive Delivery & Traffic Scaling Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.mlops.deployment import DeploymentManager, DeploymentStatus

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class DeploymentStrategy(str, Enum):
    IMMEDIATE = "IMMEDIATE"
    CANARY = "CANARY"
    BLUE_GREEN = "BLUE_GREEN"
    SHADOW = "SHADOW"
    A_B = "A_B"


class CanaryDeployment(BaseModel):
    canary_id: str = Field(default_factory=lambda: f"canary_{uuid.uuid4().hex[:10]}")
    deployment_id: str
    target_version: str
    current_traffic_percent: float = 10.0
    step_percent: float = 20.0
    max_error_rate: float = 0.05
    max_latency_ms: float = 250.0
    status: str = "IN_PROGRESS"  # IN_PROGRESS, PROMOTED, ROLLED_BACK


class BlueGreenDeployment(BaseModel):
    bg_id: str = Field(default_factory=lambda: f"bg_{uuid.uuid4().hex[:10]}")
    deployment_id: str
    blue_version: str  # Active version
    green_version: str  # New candidate version
    active_color: str = "BLUE"
    status: str = "STAGED"


class ShadowDeployment(BaseModel):
    shadow_id: str = Field(default_factory=lambda: f"shd_{uuid.uuid4().hex[:10]}")
    primary_version: str
    shadow_version: str
    mirrored_requests: int = 0
    divergence_count: int = 0


class ProgressiveDeliveryManager:
    """Manages Canary, Blue-Green, and Shadow traffic deployments with automated health guardrails."""

    def __init__(self, deployment_manager: Optional[DeploymentManager] = None) -> None:
        self.deployment_manager = deployment_manager or DeploymentManager()
        self._canaries: Dict[str, CanaryDeployment] = {}
        self._bg_deployments: Dict[str, BlueGreenDeployment] = {}
        self._shadows: Dict[str, ShadowDeployment] = {}

    def start_canary(self, deployment_id: str, target_version: str, initial_percent: float = 10.0) -> CanaryDeployment:
        canary = CanaryDeployment(
            deployment_id=deployment_id,
            target_version=target_version,
            current_traffic_percent=initial_percent,
        )
        self._canaries[canary.canary_id] = canary

        dep = self.deployment_manager.get_deployment(deployment_id)
        dep.active_traffic_percentage = initial_percent
        dep.status = DeploymentStatus.DEPLOYING

        logger.info(
            f"[PROGRESSIVE DELIVERY] Started canary for deployment '{deployment_id}' v{target_version} at {initial_percent}% traffic"
        )
        return canary

    def increase_canary_traffic(
        self, canary_id: str, error_rate: float = 0.01, latency_ms: float = 120.0
    ) -> CanaryDeployment:
        canary = self._canaries.get(canary_id)
        if not canary:
            raise KeyError(f"Canary '{canary_id}' not found")

        # Evaluate canary guardrails
        if error_rate > canary.max_error_rate or latency_ms > canary.max_latency_ms:
            canary.status = "ROLLED_BACK"
            dep = self.deployment_manager.get_deployment(canary.deployment_id)
            dep.status = DeploymentStatus.ROLLED_BACK
            logger.warning(
                f"[PROGRESSIVE DELIVERY] Canary '{canary_id}' violated guardrails (Error Rate: {error_rate:.3f}). Auto-rolling back!"
            )
            return canary

        canary.current_traffic_percent = min(100.0, canary.current_traffic_percent + canary.step_percent)
        if canary.current_traffic_percent >= 100.0:
            canary.status = "PROMOTED"
            dep = self.deployment_manager.get_deployment(canary.deployment_id)
            dep.status = DeploymentStatus.ACTIVE
            logger.info(f"[PROGRESSIVE DELIVERY] Canary '{canary_id}' successfully promoted to 100% traffic")

        return canary

    def create_blue_green(self, deployment_id: str, blue_version: str, green_version: str) -> BlueGreenDeployment:
        bg = BlueGreenDeployment(deployment_id=deployment_id, blue_version=blue_version, green_version=green_version)
        self._bg_deployments[bg.bg_id] = bg
        logger.info(
            f"[PROGRESSIVE DELIVERY] Created Blue/Green deployment (Blue: {blue_version}, Green: {green_version})"
        )
        return bg

    def switch_blue_green(self, bg_id: str) -> BlueGreenDeployment:
        bg = self._bg_deployments.get(bg_id)
        if not bg:
            raise KeyError(f"Blue/Green '{bg_id}' not found")

        bg.active_color = "GREEN" if bg.active_color == "BLUE" else "BLUE"
        bg.status = "ACTIVE"
        logger.info(
            f"[PROGRESSIVE DELIVERY] Switched Blue/Green traffic to '{bg.active_color}' ({bg.green_version if bg.active_color == 'GREEN' else bg.blue_version})"
        )
        return bg

    def start_shadow(self, primary_version: str, shadow_version: str) -> ShadowDeployment:
        shd = ShadowDeployment(primary_version=primary_version, shadow_version=shadow_version)
        self._shadows[shd.shadow_id] = shd
        logger.info(
            f"[PROGRESSIVE DELIVERY] Started shadow deployment mirroring traffic from v{primary_version} to v{shadow_version}"
        )
        return shd
