"""Feature Flag Rollout & Lifecycle Management."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.config.production_settings import FeatureFlags

logger = logging.getLogger(__name__)


class FeatureAssignment(BaseModel):
    """Assignment override of a feature flag to a tenant, organization, or workspace."""

    target_type: str  # 'tenant', 'organization', 'workspace', 'user'
    target_id: str
    enabled: bool


class FeatureRollout(BaseModel):
    """Rollout strategy specification."""

    percentage: float = 100.0  # 0.0 to 100.0
    allowed_tenant_ids: List[str] = Field(default_factory=list)
    allowed_organization_ids: List[str] = Field(default_factory=list)
    allowed_workspace_ids: List[str] = Field(default_factory=list)
    start_time: Optional[datetime] = None


class FeatureFlagConfiguration(BaseModel):
    """Managed feature flag entity."""

    flag_id: str = Field(default_factory=lambda: f"flag_{uuid.uuid4().hex[:8]}")
    name: str
    description: str = ""
    default_enabled: bool = False
    rollout: FeatureRollout = Field(default_factory=FeatureRollout)
    assignments: List[FeatureAssignment] = Field(default_factory=list)
    is_active: bool = True
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FeatureManager:
    """Manages creation, enable/disable, targeted rollouts, and rollbacks for feature flags."""

    def __init__(self) -> None:
        self._flags: Dict[str, FeatureFlagConfiguration] = {}
        # Pre-populate defaults from Phase 5.9 FeatureFlags
        defaults = FeatureFlags()
        for field, val in defaults.model_dump().items():
            self.create_feature(name=field, default_enabled=val, description=f"Default feature {field}")

    def create_feature(
        self,
        name: str,
        default_enabled: bool = False,
        description: str = "",
        rollout: Optional[FeatureRollout] = None,
    ) -> FeatureFlagConfiguration:
        """Create a new managed feature flag."""
        flag = FeatureFlagConfiguration(
            name=name,
            default_enabled=default_enabled,
            description=description,
            rollout=rollout or FeatureRollout(),
        )
        self._flags[name] = flag
        logger.info(f"[FEATURE MANAGER] Registered feature '{name}' (Enabled default: {default_enabled})")
        return flag

    def get_feature(self, name: str) -> Optional[FeatureFlagConfiguration]:
        return self._flags.get(name)

    def set_feature_enabled(self, name: str, enabled: bool) -> FeatureFlagConfiguration:
        """Globally enable or disable feature flag."""
        flag = self.get_feature(name)
        if not flag:
            flag = self.create_feature(name, default_enabled=enabled)
        flag.default_enabled = enabled
        flag.updated_at = datetime.now(timezone.utc)
        logger.info(f"[FEATURE MANAGER] Set feature '{name}' default_enabled={enabled}")
        return flag

    def configure_rollout(
        self,
        name: str,
        percentage: float = 100.0,
        tenant_ids: Optional[List[str]] = None,
        organization_ids: Optional[List[str]] = None,
        workspace_ids: Optional[List[str]] = None,
    ) -> FeatureFlagConfiguration:
        """Configure percentage and scope rollouts."""
        flag = self.get_feature(name)
        if not flag:
            flag = self.create_feature(name)

        flag.rollout.percentage = max(0.0, min(100.0, percentage))
        if tenant_ids is not None:
            flag.rollout.allowed_tenant_ids = tenant_ids
        if organization_ids is not None:
            flag.rollout.allowed_organization_ids = organization_ids
        if workspace_ids is not None:
            flag.rollout.allowed_workspace_ids = workspace_ids

        flag.updated_at = datetime.now(timezone.utc)
        logger.info(f"[FEATURE MANAGER] Updated rollout for feature '{name}' ({percentage}%)")
        return flag

    def rollback_feature(self, name: str) -> Optional[FeatureFlagConfiguration]:
        """Rollback feature rollout to completely disabled state."""
        flag = self.get_feature(name)
        if flag:
            flag.default_enabled = False
            flag.rollout = FeatureRollout(percentage=0.0)
            flag.assignments = []
            flag.updated_at = datetime.now(timezone.utc)
            logger.warning(f"[FEATURE MANAGER] Rolled back feature '{name}'")
        return flag

    def list_features(self) -> List[FeatureFlagConfiguration]:
        return list(self._flags.values())
