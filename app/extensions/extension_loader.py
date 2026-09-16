"""Extension Loader initializing manifests and runtime handlers."""

import logging
from typing import Any, Dict

from app.extensions.extension import Extension, ExtensionManifest

logger = logging.getLogger(__name__)


class ExtensionLoader:
    """Validates manifests and loads extension instances."""

    def load_extension_from_manifest(
        self,
        manifest_dict: Dict[str, Any],
        tenant_id: str = "global",
        developer_id: str = "system",
    ) -> Extension:
        """Parse, validate manifest, and build extension model."""
        manifest = ExtensionManifest(**manifest_dict)
        manifest.validate_manifest()

        ext = Extension(
            manifest=manifest,
            tenant_id=tenant_id,
            developer_id=developer_id,
            current_version=manifest.version,
            is_enabled=False,
        )
        logger.info(f"[EXTENSION LOADER] Loaded extension '{manifest.name}' v{manifest.version}")
        return ext
