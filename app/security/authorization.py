"""Authorization Engine for Policy, RBAC & Isolation Enforcement."""

import logging
from typing import Dict, Any, List, Optional, Union
from app.security.identity import Identity
from app.security.exceptions import (
    PermissionDeniedError, TenantAccessDeniedError, AuthorizationError
)

logger = logging.getLogger(__name__)


class AuthorizationEngine:
    """Enforces fine-grained RBAC, scope validation, and multi-tenant isolation."""

    def __init__(self) -> None:
        pass

    def has_role(self, identity: Identity, required_role: str) -> bool:
        """Check if identity possesses required role."""
        return identity.has_role(required_role)

    def has_scope(self, identity: Identity, required_scope: str) -> bool:
        """Check if identity possesses required API scope."""
        return identity.has_scope(required_scope)

    def has_permission(self, identity: Identity, required_permission: str) -> bool:
        """Check if identity possesses required granular permission."""
        return identity.has_permission(required_permission)

    def validate_tenant_access(
        self,
        identity: Identity,
        resource_tenant_id: Optional[str],
        allow_global: bool = True,
    ) -> bool:
        """Validate multi-tenant isolation boundary."""
        if identity.is_admin or "system" in identity.roles or identity.tenant_id == "system":
            return True

        if not resource_tenant_id:
            return True

        if allow_global and resource_tenant_id in ("global", "default_tenant"):
            return True

        if identity.tenant_id == resource_tenant_id:
            return True

        logger.warning(
            f"[TENANT ISOLATION VIOLATION] Identity '{identity.identity_id}' (tenant={identity.tenant_id}) "
            f"attempted cross-tenant access to resource (tenant={resource_tenant_id})"
        )
        raise TenantAccessDeniedError(
            f"Tenant '{identity.tenant_id}' cannot access resource belonging to tenant '{resource_tenant_id}'"
        )

    def validate_resource_access(
        self,
        identity: Identity,
        resource: Dict[str, Any],
        required_permission: Optional[str] = None,
        required_scope: Optional[str] = None,
    ) -> bool:
        """Validate identity against resource tenant, organization, and workspace boundaries."""
        # 1. Tenant check
        res_tenant = resource.get("tenant_id")
        self.validate_tenant_access(identity, res_tenant)

        # 2. Org check if specified on resource
        res_org = resource.get("organization_id")
        if res_org and identity.organization_id and not identity.is_admin:
            if identity.organization_id != res_org and identity.tenant_id != "system":
                raise AuthorizationError(f"Access denied to organization '{res_org}'")

        # 3. Workspace check if specified on resource
        res_ws = resource.get("workspace_id")
        if res_ws and identity.workspace_id and not identity.is_admin:
            if identity.workspace_id != res_ws and identity.tenant_id != "system":
                raise AuthorizationError(f"Access denied to workspace '{res_ws}'")

        # 4. Scope check
        if required_scope and not self.has_scope(identity, required_scope):
            raise PermissionDeniedError(f"Missing required scope '{required_scope}'")

        # 5. Permission check
        if required_permission and not self.has_permission(identity, required_permission):
            raise PermissionDeniedError(f"Missing required permission '{required_permission}'")

        return True

    def authorize(
        self,
        identity: Identity,
        required_roles: Optional[List[str]] = None,
        required_scopes: Optional[List[str]] = None,
        required_permissions: Optional[List[str]] = None,
        target_tenant_id: Optional[str] = None,
    ) -> bool:
        """Comprehensive authorization assertion."""
        # Tenant boundary
        if target_tenant_id:
            self.validate_tenant_access(identity, target_tenant_id)

        # Role check (any match)
        if required_roles:
            if not any(self.has_role(identity, r) for r in required_roles):
                raise PermissionDeniedError(f"Required one of roles: {required_roles}")

        # Scope check (all match)
        if required_scopes:
            for s in required_scopes:
                if not self.has_scope(identity, s):
                    raise PermissionDeniedError(f"Missing required scope: {s}")

        # Permission check (all match)
        if required_permissions:
            for p in required_permissions:
                if not self.has_permission(identity, p):
                    raise PermissionDeniedError(f"Missing required permission: {p}")

        return True
