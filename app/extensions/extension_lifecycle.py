"""Extension Lifecycle State Machine with Atomic Upgrade & Rollback."""

import logging
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.extensions.extension import Extension, ExtensionVersion
from app.extensions.exceptions import InvalidExtensionLifecycleTransition

logger = logging.getLogger(__name__)


class ExtensionLifecycleState(str, Enum):
    INSTALLED = "INSTALLED"
    ENABLED = "ENABLED"
    DISABLED = "DISABLED"
    UPDATING = "UPDATING"
    FAILED = "FAILED"
    DEPRECATED = "DEPRECATED"
    UNINSTALLED = "UNINSTALLED"


VALID_EXTENSION_TRANSITIONS = {
    ExtensionLifecycleState.INSTALLED: {ExtensionLifecycleState.ENABLED, ExtensionLifecycleState.DISABLED, ExtensionLifecycleState.UNINSTALLED, ExtensionLifecycleState.FAILED},
    ExtensionLifecycleState.ENABLED: {ExtensionLifecycleState.DISABLED, ExtensionLifecycleState.UPDATING, ExtensionLifecycleState.DEPRECATED, ExtensionLifecycleState.FAILED},
    ExtensionLifecycleState.DISABLED: {ExtensionLifecycleState.ENABLED, ExtensionLifecycleState.UPDATING, ExtensionLifecycleState.UNINSTALLED, ExtensionLifecycleState.DEPRECATED},
    ExtensionLifecycleState.UPDATING: {ExtensionLifecycleState.ENABLED, ExtensionLifecycleState.FAILED, ExtensionLifecycleState.DISABLED},
    ExtensionLifecycleState.FAILED: {ExtensionLifecycleState.UPDATING, ExtensionLifecycleState.DISABLED, ExtensionLifecycleState.UNINSTALLED},
    ExtensionLifecycleState.DEPRECATED: {ExtensionLifecycleState.DISABLED, ExtensionLifecycleState.UNINSTALLED},
    ExtensionLifecycleState.UNINSTALLED: set(),
}


class ExtensionLifecycleManager:
    """Enforces valid extension state transitions and handles version upgrades and atomic rollbacks."""

    def __init__(self) -> None:
        self._states: Dict[str, ExtensionLifecycleState] = {}

    def get_state(self, extension_id: str) -> ExtensionLifecycleState:
        return self._states.get(extension_id, ExtensionLifecycleState.INSTALLED)

    def transition(self, extension: Extension, target_state: ExtensionLifecycleState, reason: str = "Transition") -> ExtensionLifecycleState:
        current = self.get_state(extension.extension_id)
        if current != target_state and target_state not in VALID_EXTENSION_TRANSITIONS.get(current, set()):
            raise InvalidExtensionLifecycleTransition(current.value, target_state.value)

        self._states[extension.extension_id] = target_state
        extension.status = target_state.value
        extension.is_enabled = target_state == ExtensionLifecycleState.ENABLED
        extension.updated_at = datetime.now(timezone.utc)
        logger.info(f"[EXTENSION LIFECYCLE] '{extension.extension_id}' transitioned {current.value} -> {target_state.value}")
        return target_state

    def enable_extension(self, extension: Extension) -> ExtensionLifecycleState:
        return self.transition(extension, ExtensionLifecycleState.ENABLED, "Enable extension")

    def disable_extension(self, extension: Extension) -> ExtensionLifecycleState:
        return self.transition(extension, ExtensionLifecycleState.DISABLED, "Disable extension")

    def upgrade_extension(self, extension: Extension, new_version: ExtensionVersion) -> ExtensionVersion:
        """Atomic upgrade to a new extension version."""
        prev_version_str = extension.current_version
        self.transition(extension, ExtensionLifecycleState.UPDATING, f"Upgrading from {prev_version_str} to {new_version.version_number}")

        try:
            extension.versions.append(new_version)
            extension.manifest = new_version.manifest
            extension.current_version = new_version.version_number
            self.transition(extension, ExtensionLifecycleState.ENABLED, "Upgrade completed")
            logger.info(f"[EXTENSION UPGRADE] Successfully upgraded '{extension.extension_id}' to v{new_version.version_number}")
            return new_version
        except Exception as e:
            logger.error(f"[EXTENSION UPGRADE FAILED] Upgrade failed for '{extension.extension_id}': {e}. Initiating rollback...")
            self.rollback_extension(extension, prev_version_str)
            raise

    def rollback_extension(self, extension: Extension, target_version_str: str) -> Extension:
        """Rollback extension to a previous version number."""
        matched = next((v for v in extension.versions if v.version_number == target_version_str), None)
        if not matched:
            raise RuntimeError(f"Version '{target_version_str}' not found in history for extension '{extension.extension_id}'")

        extension.manifest = matched.manifest
        extension.current_version = matched.version_number
        self.transition(extension, ExtensionLifecycleState.ENABLED, f"Rolled back to {target_version_str}")
        logger.warning(f"[EXTENSION ROLLBACK] Rolled back '{extension.extension_id}' to v{target_version_str}")
        return extension
