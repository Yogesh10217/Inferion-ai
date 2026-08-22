"""Deterministic Feature Evaluator across multi-level context scopes."""

import hashlib
import logging
from typing import Dict, Any, Optional
from app.control_plane.feature_management import FeatureManager, FeatureFlagConfiguration

logger = logging.getLogger(__name__)


class FeatureEvaluator:
    """Evaluates feature flag status deterministically across Platform -> Tenant -> Organization -> Workspace -> User."""

    def __init__(self, manager: Optional[FeatureManager] = None) -> None:
        self.manager = manager or FeatureManager()

    def is_feature_enabled(
        self,
        feature_name: str,
        tenant_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> bool:
        """Evaluate if feature is enabled for given context scopes."""
        flag = self.manager.get_feature(feature_name)
        if not flag or not flag.is_active:
            return False

        # 1. Direct explicit assignment overrides
        if user_id:
            user_assign = next((a for a in flag.assignments if a.target_type == "user" and a.target_id == user_id), None)
            if user_assign:
                return user_assign.enabled

        if workspace_id:
            ws_assign = next((a for a in flag.assignments if a.target_type == "workspace" and a.target_id == workspace_id), None)
            if ws_assign:
                return ws_assign.enabled

        if organization_id:
            org_assign = next((a for a in flag.assignments if a.target_type == "organization" and a.target_id == organization_id), None)
            if org_assign:
                return org_assign.enabled

        if tenant_id:
            tenant_assign = next((a for a in flag.assignments if a.target_type == "tenant" and a.target_id == tenant_id), None)
            if tenant_assign:
                return tenant_assign.enabled

        # 2. Targeted scope lists
        if tenant_id and flag.rollout.allowed_tenant_ids:
            if tenant_id in flag.rollout.allowed_tenant_ids:
                return True

        if organization_id and flag.rollout.allowed_organization_ids:
            if organization_id in flag.rollout.allowed_organization_ids:
                return True

        if workspace_id and flag.rollout.allowed_workspace_ids:
            if workspace_id in flag.rollout.allowed_workspace_ids:
                return True

        # 3. Percentage rollout check (deterministic hashing by entity ID)
        if flag.rollout.percentage < 100.0:
            seed = f"{feature_name}:{tenant_id or 'global'}:{user_id or 'anon'}"
            hash_val = int(hashlib.sha256(seed.encode()).hexdigest(), 16) % 100
            if hash_val >= flag.rollout.percentage:
                return False

        # 4. Fallback to default
        return flag.default_enabled
