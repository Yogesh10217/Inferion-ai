"""Hierarchical Configuration Engine with Snapshot Rollback & Scope Inheritance."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.control_plane.exceptions import ConfigurationException

logger = logging.getLogger(__name__)


class ConfigurationScope(str, Enum):
    PLATFORM = "PLATFORM"
    TENANT = "TENANT"
    ORGANIZATION = "ORGANIZATION"
    WORKSPACE = "WORKSPACE"
    RESOURCE = "RESOURCE"


class ConfigurationVersion(BaseModel):
    """Immutable version snapshot of configuration."""

    version_id: str = Field(default_factory=lambda: f"ver_{uuid.uuid4().hex[:10]}")
    version_number: int
    scope: ConfigurationScope
    scope_target_id: str
    settings: Dict[str, Any]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = "system"
    commit_message: str = "Configuration update"


class ConfigurationSnapshot(BaseModel):
    """Full snapshot across scopes for auditing and rollback."""

    snapshot_id: str = Field(default_factory=lambda: f"snp_{uuid.uuid4().hex[:10]}")
    scope: ConfigurationScope
    target_id: str
    active_version_id: str
    settings: Dict[str, Any]
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConfigurationManager:
    """Manages hierarchical configuration inheritance, versioning, snapshots, and rollbacks."""

    def __init__(self) -> None:
        # Key: (scope, target_id) -> list of ConfigurationVersion
        self._versions: Dict[str, List[ConfigurationVersion]] = {}
        # Key: (scope, target_id) -> active settings dict
        self._active_configs: Dict[str, Dict[str, Any]] = {}

    def _build_key(self, scope: ConfigurationScope, target_id: str) -> str:
        return f"{scope.value}:{target_id}"

    def update_configuration(
        self,
        scope: ConfigurationScope,
        target_id: str,
        settings_update: Dict[str, Any],
        actor_id: str = "admin",
        commit_message: str = "Update configuration",
    ) -> ConfigurationVersion:
        """Apply new configuration values, creating a new immutable version."""
        key = self._build_key(scope, target_id)
        if key not in self._versions:
            self._versions[key] = []
            self._active_configs[key] = {}

        history = self._versions[key]
        current = self._active_configs[key]

        new_settings = dict(current)
        new_settings.update(settings_update)
        self._active_configs[key] = new_settings

        ver_num = len(history) + 1
        version = ConfigurationVersion(
            version_number=ver_num,
            scope=scope,
            scope_target_id=target_id,
            settings=new_settings,
            created_by=actor_id,
            commit_message=commit_message,
        )
        history.append(version)
        logger.info(f"[CONFIG MANAGER] Updated config scope '{scope.value}' (target: {target_id}, version: v{ver_num})")
        return version

    def get_configuration(
        self,
        scope: ConfigurationScope,
        target_id: str,
        parent_configs: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Get resolved configuration with scope inheritance overriding."""
        resolved: Dict[str, Any] = {}

        # 1. Inherit from higher scopes if provided (Platform -> Tenant -> Org -> Workspace -> Resource)
        if parent_configs:
            for p_cfg in parent_configs:
                resolved.update(p_cfg)

        # 2. Apply target scope config
        key = self._build_key(scope, target_id)
        active = self._active_configs.get(key, {})
        resolved.update(active)

        return resolved

    def rollback_configuration(
        self,
        scope: ConfigurationScope,
        target_id: str,
        target_version_number: int,
        actor_id: str = "admin",
    ) -> ConfigurationVersion:
        """Rollback configuration to a previous version number."""
        key = self._build_key(scope, target_id)
        if key not in self._versions:
            raise ConfigurationException(f"No configuration history found for scope '{scope.value}:{target_id}'")

        history = self._versions[key]
        target_ver = next((v for v in history if v.version_number == target_version_number), None)
        if not target_ver:
            raise ConfigurationException(f"Version number '{target_version_number}' not found")

        # Rollback applies target version settings as new version
        return self.update_configuration(
            scope=scope,
            target_id=target_id,
            settings_update=target_ver.settings,
            actor_id=actor_id,
            commit_message=f"Rollback to version v{target_version_number}",
        )

    def list_versions(self, scope: ConfigurationScope, target_id: str) -> List[ConfigurationVersion]:
        """Get full version history for scope and target."""
        key = self._build_key(scope, target_id)
        return list(self._versions.get(key, []))

    def create_snapshot(self, scope: ConfigurationScope, target_id: str) -> ConfigurationSnapshot:
        """Capture explicit configuration snapshot."""
        key = self._build_key(scope, target_id)
        history = self._versions.get(key, [])
        active_ver_id = history[-1].version_id if history else "v0"
        active_cfg = self._active_configs.get(key, {})

        return ConfigurationSnapshot(
            scope=scope,
            target_id=target_id,
            active_version_id=active_ver_id,
            settings=dict(active_cfg),
        )
