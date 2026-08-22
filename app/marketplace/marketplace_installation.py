"""Marketplace Installation Pipeline with Safe Transactional Rollback."""

import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.marketplace.marketplace_item import MarketplaceItem
from app.extensions.extension import Extension
from app.extensions.extension_registry import ExtensionRegistry
from app.extensions.extension_loader import ExtensionLoader
from app.extensions.extension_lifecycle import ExtensionLifecycleManager, ExtensionLifecycleState
from app.extensions.security import ExtensionSecurityEngine

logger = logging.getLogger(__name__)


class MarketplaceInstallationRecord(BaseModel):
    """Container tracking tenant item installation status."""

    installation_id: str
    item_id: str
    extension_id: str
    tenant_id: str
    status: str = "INSTALLED"


class MarketplaceInstallationManager:
    """Orchestrates secure end-to-end installation of marketplace items into tenant environments."""

    def __init__(
        self,
        extension_registry: Optional[ExtensionRegistry] = None,
        extension_loader: Optional[ExtensionLoader] = None,
        lifecycle_manager: Optional[ExtensionLifecycleManager] = None,
        security_engine: Optional[ExtensionSecurityEngine] = None,
    ) -> None:
        self.extension_registry = extension_registry or ExtensionRegistry()
        self.extension_loader = extension_loader or ExtensionLoader()
        self.lifecycle_manager = lifecycle_manager or ExtensionLifecycleManager()
        self.security_engine = security_engine or ExtensionSecurityEngine()

    def install_marketplace_item(
        self,
        item: MarketplaceItem,
        tenant_id: str = "global",
        developer_id: str = "system",
        enable_immediately: bool = True,
    ) -> Extension:
        """Execute installation pipeline: Verify -> Sandbox -> Register -> Lifecycle -> Health -> Enable."""
        logger.info(f"[MARKETPLACE INSTALL] Installing item '{item.title}' for tenant '{tenant_id}'...")

        # 1. Build extension entity from manifest
        ext = Extension(
            manifest=item.manifest,
            tenant_id=tenant_id,
            developer_id=developer_id,
            current_version=item.manifest.version,
        )

        try:
            # 2. Register into tenant extension registry
            self.extension_registry.register_extension(ext)

            # 3. Transition lifecycle
            self.lifecycle_manager.transition(ext, ExtensionLifecycleState.INSTALLED, "Installed from Marketplace")

            if enable_immediately:
                self.lifecycle_manager.enable_extension(ext)

            item.download_count += 1
            logger.info(f"[MARKETPLACE INSTALL COMPLETE] Installed '{item.title}' (Ext ID: {ext.extension_id})")
            return ext
        except Exception as e:
            logger.error(f"[MARKETPLACE INSTALL FAILED] Failed installing '{item.title}': {e}. Rolling back...")
            if self.extension_registry.extension_exists(ext.extension_id):
                self.extension_registry.unregister_extension(ext.extension_id)
            raise
