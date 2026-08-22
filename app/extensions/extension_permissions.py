"""Extension Permission Engine blocking capability escalation and enforcing scope isolation."""

import logging
from typing import Dict, Any, List, Optional
from app.extensions.extension import Extension
from app.extensions.exceptions import ExtensionSecurityViolationException

logger = logging.getLogger(__name__)


class ExtensionPermissionEngine:
    """Validates extension capability bounds and prevents capability escalation."""

    @staticmethod
    def validate_extension_permissions(
        extension: Extension,
        requested_action: str,
        tenant_id: str = "global",
        context: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Validate if extension is authorized to perform requested_action within tenant scope."""

        # 1. Multi-Tenant scope isolation
        if extension.tenant_id not in (tenant_id, "global"):
            raise ExtensionSecurityViolationException(
                f"Cross-tenant violation: Extension '{extension.extension_id}' belonging to tenant '{extension.tenant_id}' cannot execute in tenant '{tenant_id}'"
            )

        # 2. Scope validation against required permissions
        manifest = extension.manifest
        req_perms = manifest.required_permissions

        if requested_action == "network:external" and not manifest.runtime_requirements.allow_network_access:
            raise ExtensionSecurityViolationException("Unpermitted action: Network access is disabled in extension manifest")

        if requested_action == "filesystem:write" and not manifest.runtime_requirements.allow_filesystem_access:
            raise ExtensionSecurityViolationException("Unpermitted action: Filesystem write access is disabled in extension manifest")

        if requested_action in ("secret:read", "admin:all") and requested_action not in req_perms:
            raise ExtensionSecurityViolationException(f"Permission escalation blocked: Extension lacks required permission '{requested_action}'")

        logger.info(f"[EXTENSION PERMISSION] Authorized action '{requested_action}' for extension '{extension.extension_id}'")
        return True
