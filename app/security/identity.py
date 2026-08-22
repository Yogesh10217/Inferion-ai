"""Enterprise Identity Models."""

from typing import Dict, List, Optional, Any, Set
from enum import Enum
from pydantic import BaseModel, Field


class AuthenticationMethod(str, Enum):
    JWT = "jwt"
    API_KEY = "api_key"
    SERVICE = "service"
    SYSTEM = "system"
    ANONYMOUS = "anonymous"


class Identity(BaseModel):
    """Base identity representing an authenticated or context principal."""

    identity_id: str
    identity_type: str = "base"
    user_id: Optional[str] = None
    service_id: Optional[str] = None
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    roles: Set[str] = Field(default_factory=set)
    scopes: Set[str] = Field(default_factory=set)
    permissions: Set[str] = Field(default_factory=set)
    authentication_method: AuthenticationMethod = AuthenticationMethod.ANONYMOUS
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    is_admin: bool = False

    def has_role(self, role: str) -> bool:
        return "admin" in self.roles or self.is_admin or role in self.roles

    def has_scope(self, scope: str) -> bool:
        if "*" in self.scopes or "admin" in self.roles or self.is_admin:
            return True
        return scope in self.scopes

    def has_permission(self, permission: str) -> bool:
        if "*" in self.permissions or "admin" in self.roles or self.is_admin:
            return True
        return permission in self.permissions


class UserIdentity(Identity):
    """User principal identity."""

    identity_type: str = "user"
    username: Optional[str] = None
    email: Optional[str] = None

    @classmethod
    def create(
        cls,
        user_id: str,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        roles: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
        scopes: Optional[List[str]] = None,
        email: Optional[str] = None,
        username: Optional[str] = None,
        is_admin: bool = False,
    ) -> "UserIdentity":
        return cls(
            identity_id=f"user:{user_id}",
            user_id=user_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            roles=set(roles or []),
            permissions=set(permissions or []),
            scopes=set(scopes or []),
            email=email,
            username=username,
            is_admin=is_admin,
            authentication_method=AuthenticationMethod.JWT,
        )


class ServiceIdentity(Identity):
    """Service-to-service principal identity."""

    identity_type: str = "service"

    @classmethod
    def create(
        cls,
        service_id: str,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        scopes: Optional[List[str]] = None,
    ) -> "ServiceIdentity":
        return cls(
            identity_id=f"service:{service_id}",
            service_id=service_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            scopes=set(scopes or ["service"]),
            authentication_method=AuthenticationMethod.SERVICE,
        )


class APIKeyIdentity(Identity):
    """API Key principal identity."""

    identity_type: str = "api_key"
    key_id: str
    key_prefix: str

    @classmethod
    def create(
        cls,
        key_id: str,
        key_prefix: str,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        permissions: Optional[List[str]] = None,
    ) -> "APIKeyIdentity":
        return cls(
            identity_id=f"key:{key_id}",
            key_id=key_id,
            key_prefix=key_prefix,
            user_id=user_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            scopes=set(scopes or []),
            permissions=set(permissions or []),
            authentication_method=AuthenticationMethod.API_KEY,
        )


class SystemIdentity(Identity):
    """Internal system engine principal identity."""

    identity_type: str = "system"

    @classmethod
    def create(cls, system_name: str = "llm_engine") -> "SystemIdentity":
        return cls(
            identity_id=f"system:{system_name}",
            tenant_id="system",
            roles={"admin", "system"},
            permissions={"*"},
            scopes={"*"},
            is_admin=True,
            authentication_method=AuthenticationMethod.SYSTEM,
        )
