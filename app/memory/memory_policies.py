"""
Memory Security & Policy Engine: RBAC & Tenant Isolation Guards
"""

from typing import List, Optional

from app.memory.exceptions import MemoryRBACPermissionDeniedError, TenantMemoryIsolationError


class MemoryPolicyEngine:
    """Enforces multi-tenant isolation, workspace scoping, and RBAC guards for memory access."""

    @staticmethod
    def validate_tenant_access(
        request_org: str,
        target_org: str,
        request_workspace: Optional[str] = None,
        target_workspace: Optional[str] = None,
    ) -> None:
        if not request_org or request_org != target_org:
            raise TenantMemoryIsolationError(f"Cross-tenant access blocked: '{request_org}' != '{target_org}'")
        if target_workspace and request_workspace and request_workspace != target_workspace:
            raise TenantMemoryIsolationError(
                f"Cross-workspace access blocked: '{request_workspace}' != '{target_workspace}'"
            )

    @staticmethod
    def validate_rbac(user_roles: List[str], required_permission: str = "read") -> None:
        if "admin" in user_roles or "owner" in user_roles:
            return
        if required_permission == "write" and "viewer" in user_roles and "developer" not in user_roles:
            raise MemoryRBACPermissionDeniedError("Viewer role lacks write permission for memory operations")
