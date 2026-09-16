"""Multi-tenant Thread-Safe Extension Registry."""

import logging
import threading
from typing import Dict, List, Optional

from app.extensions.exceptions import ExtensionNotFoundException
from app.extensions.extension import Extension, ExtensionType

logger = logging.getLogger(__name__)


class ExtensionRegistry:
    """Thread-safe multi-tenant extension inventory and registry."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._extensions: Dict[str, Extension] = {}

    def register_extension(self, extension: Extension) -> Extension:
        """Register or update an extension in the registry."""
        with self._lock:
            extension.manifest.validate_manifest()
            self._extensions[extension.extension_id] = extension
            logger.info(f"[EXTENSION REGISTRY] Registered extension '{extension.manifest.name}' (ID: {extension.extension_id}, Tenant: {extension.tenant_id})")
            return extension

    def unregister_extension(self, extension_id: str) -> bool:
        """Unregister an extension."""
        with self._lock:
            if extension_id not in self._extensions:
                raise ExtensionNotFoundException(extension_id)
            del self._extensions[extension_id]
            logger.info(f"[EXTENSION REGISTRY] Unregistered extension '{extension_id}'")
            return True

    def get_extension(self, extension_id: str) -> Extension:
        """Get extension by ID."""
        with self._lock:
            ext = self._extensions.get(extension_id)
            if not ext:
                raise ExtensionNotFoundException(extension_id)
            return ext

    def extension_exists(self, extension_id: str) -> bool:
        with self._lock:
            return extension_id in self._extensions

    def list_extensions(
        self,
        tenant_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        extension_type: Optional[ExtensionType] = None,
        enabled_only: bool = False,
    ) -> List[Extension]:
        """List extensions matching tenant and scope filters."""
        with self._lock:
            res = list(self._extensions.values())
            if tenant_id:
                res = [e for e in res if e.tenant_id in (tenant_id, "global")]
            if organization_id:
                res = [e for e in res if e.organization_id is None or e.organization_id == organization_id]
            if workspace_id:
                res = [e for e in res if e.workspace_id is None or e.workspace_id == workspace_id]
            if extension_type:
                res = [e for e in res if e.manifest.extension_type == extension_type]
            if enabled_only:
                res = [e for e in res if e.is_enabled]
            return res

    def search_extensions(self, query: str, tenant_id: Optional[str] = None) -> List[Extension]:
        """Search extensions by query term."""
        q_norm = query.lower()
        res_list = self.list_extensions(tenant_id=tenant_id)
        return [
            e for e in res_list
            if q_norm in e.manifest.name.lower()
            or q_norm in e.manifest.identifier.lower()
            or q_norm in e.manifest.description.lower()
        ]
