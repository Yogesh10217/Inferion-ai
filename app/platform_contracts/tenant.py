"""Tenant Isolation Primitives & Access Guards (Phase 5.30)."""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.platform_contracts.exceptions import CrossTenantAccessException


class TenantReference(BaseModel):
    tenant_id: str
    organization_id: Optional[str] = None


class TenantContext(BaseModel):
    tenant_id: str
    principal_id: Optional[str] = None
    is_global_admin: bool = False


class TenantScopedResource(BaseModel):
    resource_id: str
    tenant_id: str
    resource_type: str


class TenantIsolationValidator:
    """Validates tenant isolation boundaries cleanly and safely."""

    @staticmethod
    def validate_tenant_access(requester_tenant_id: str, resource_tenant_id: str) -> bool:
        if requester_tenant_id == "global" or resource_tenant_id == "global":
            return True
        if requester_tenant_id != resource_tenant_id:
            raise CrossTenantAccessException(requester_tenant_id, resource_tenant_id)
        return True


class TenantAccessGuard:
    """Helper guard wrapping tenant isolation checks."""

    def __init__(self, validator: Optional[TenantIsolationValidator] = None) -> None:
        self.validator = validator or TenantIsolationValidator()

    def enforce_isolation(self, requester_tenant_id: str, resource_tenant_id: str) -> None:
        self.validator.validate_tenant_access(requester_tenant_id, resource_tenant_id)
