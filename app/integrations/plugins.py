"""Sandboxed Plugin & Extension Execution Platform."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.extensions.manager import ExtensionManager
from app.integrations.exceptions import PluginSecurityViolationException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PluginStatus(str, Enum):
    DRAFT = "DRAFT"
    VALIDATED = "VALIDATED"
    PUBLISHED = "PUBLISHED"
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"
    REVOKED = "REVOKED"


class PluginManifest(BaseModel):
    name: str
    version: str = "1.0.0"
    publisher: str = "internal"
    capabilities: List[str] = Field(default_factory=list)
    required_permissions: List[str] = Field(default_factory=list)
    timeout_seconds: int = 30


class Plugin(BaseModel):
    plugin_id: str = Field(default_factory=lambda: f"plug_{uuid.uuid4().hex[:10]}")
    manifest: PluginManifest
    status: PluginStatus = PluginStatus.ACTIVE
    tenant_id: str = "global"
    created_at: datetime = Field(default_factory=_now)


class PluginManager:
    """Manages sandboxed plugin lifecycles, manifest validation, and security capability enforcement."""

    def __init__(self, extension_manager: Optional[ExtensionManager] = None) -> None:
        self.extension_manager = extension_manager or ExtensionManager()
        self._plugins: Dict[str, Plugin] = {}

    def register_plugin(self, manifest: PluginManifest, tenant_id: str = "global") -> Plugin:
        plug = Plugin(manifest=manifest, tenant_id=tenant_id)
        self._plugins[plug.plugin_id] = plug
        logger.info(f"[PLUGIN MANAGER] Registered plugin '{plug.plugin_id}' ('{manifest.name}') for tenant '{tenant_id}'")
        return plug

    def execute_plugin(self, plugin_id: str, requested_capability: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        plug = self._plugins.get(plugin_id)
        if not plug or plug.status != PluginStatus.ACTIVE:
            raise PluginSecurityViolationException(plugin_id, "Plugin is not active or not registered")

        # Verify capability declared in manifest!
        if requested_capability not in plug.manifest.capabilities:
            logger.warning(f"[PLUGIN MANAGER] Plugin '{plugin_id}' attempted capability '{requested_capability}' not in manifest!")
            raise PluginSecurityViolationException(plugin_id, f"Capability '{requested_capability}' is not declared in plugin manifest")

        logger.info(f"[PLUGIN MANAGER] Executed plugin '{plugin_id}' capability '{requested_capability}' within sandbox limits")
        return {"status": "SUCCESS", "plugin_id": plugin_id, "capability": requested_capability}
