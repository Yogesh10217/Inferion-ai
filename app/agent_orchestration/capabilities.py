"""Agent Capability Discovery & Validation Subsystem (Phase 5.36)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Set

from pydantic import BaseModel, Field

from app.agent_orchestration.exceptions import (
    AgentCapabilityViolationException,
    CrossTenantAgentAccessException,
)
from app.platform_contracts.tenant import TenantAccessGuard


class CapabilityScope(str, Enum):
    READ = "READ"
    ANALYZE = "ANALYZE"
    PLAN = "PLAN"
    RECOMMEND = "RECOMMEND"
    DELEGATE = "DELEGATE"
    EXECUTE_WITH_APPROVAL = "EXECUTE_WITH_APPROVAL"


class CapabilityPermission(BaseModel):
    permission_name: str
    target_resource_pattern: str = "*"
    action: str = "read"


class CapabilityConstraint(BaseModel):
    allowed_target_systems: List[str] = Field(default_factory=lambda: ["*"])
    max_data_classification: str = "CONFIDENTIAL"
    requires_approval_for_write: bool = True


class AgentCapabilityDefinition(BaseModel):
    capability_id: str = Field(default_factory=lambda: f"cap_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    description: str = ""
    scopes: Set[CapabilityScope] = Field(default_factory=lambda: {CapabilityScope.READ, CapabilityScope.ANALYZE})
    permissions: List[CapabilityPermission] = Field(default_factory=list)
    constraint: CapabilityConstraint = Field(default_factory=CapabilityConstraint)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CapabilityValidationResult(BaseModel):
    is_valid: bool
    capability_name: str
    evaluated_scope: CapabilityScope
    missing_scopes: List[CapabilityScope] = Field(default_factory=list)
    violations: List[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentCapabilityManager:
    """Manages capability registration, discovery, and strict authorization validation."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._capabilities: Dict[str, AgentCapabilityDefinition] = {}

    def register_capability(
        self,
        tenant_id: str,
        name: str,
        description: str = "",
        scopes: Optional[Set[CapabilityScope]] = None,
        permissions: Optional[List[CapabilityPermission]] = None,
        constraint: Optional[CapabilityConstraint] = None,
        capability_id: Optional[str] = None,
    ) -> AgentCapabilityDefinition:
        cap_id = capability_id or f"cap_{uuid.uuid4().hex[:12]}"
        cap = AgentCapabilityDefinition(
            capability_id=cap_id,
            tenant_id=tenant_id,
            name=name,
            description=description,
            scopes=scopes or {CapabilityScope.READ, CapabilityScope.ANALYZE},
            permissions=permissions or [],
            constraint=constraint or CapabilityConstraint(),
        )
        self._capabilities[cap.capability_id] = cap
        return cap

    def get_capability(self, capability_id: str, tenant_id: str) -> AgentCapabilityDefinition:
        cap = self._capabilities.get(capability_id)
        if not cap:
            try:
                scope_enum = CapabilityScope(capability_id)
                return AgentCapabilityDefinition(
                    capability_id=capability_id,
                    tenant_id=tenant_id,
                    name=f"Standard {capability_id} Capability",
                    scopes={scope_enum, CapabilityScope.READ, CapabilityScope.ANALYZE, CapabilityScope.PLAN, CapabilityScope.RECOMMEND, CapabilityScope.DELEGATE, CapabilityScope.EXECUTE_WITH_APPROVAL},
                )
            except Exception:
                raise AgentCapabilityViolationException(f"Capability '{capability_id}' not found.")

        try:
            self.tenant_guard.enforce_isolation(tenant_id, cap.tenant_id)
        except Exception:
            raise CrossTenantAgentAccessException(tenant_id, cap.tenant_id)

        return cap

    def list_capabilities(self, tenant_id: str) -> List[AgentCapabilityDefinition]:
        return [c for c in self._capabilities.values() if c.tenant_id == tenant_id or tenant_id == "global"]

    def validate_capability(
        self,
        capability_id: str,
        tenant_id: str,
        required_scope: CapabilityScope,
        target_system: Optional[str] = None,
        data_classification: Optional[str] = None,
    ) -> CapabilityValidationResult:
        cap = self.get_capability(capability_id, tenant_id)
        violations = []

        if not cap.is_active:
            violations.append(f"Capability '{cap.name}' is inactive.")

        if required_scope not in cap.scopes:
            violations.append(f"Scope '{required_scope.value}' is not granted in capability '{cap.name}'.")

        if target_system and "*" not in cap.constraint.allowed_target_systems:
            if target_system not in cap.constraint.allowed_target_systems:
                violations.append(f"Target system '{target_system}' is not allowed for capability '{cap.name}'.")

        is_valid = len(violations) == 0
        return CapabilityValidationResult(
            is_valid=is_valid,
            capability_name=cap.name,
            evaluated_scope=required_scope,
            violations=violations,
        )

    def validate_agent_capabilities(
        self,
        agent_capabilities: List[str],
        tenant_id: str,
        required_scope: CapabilityScope,
        target_system: Optional[str] = None,
    ) -> bool:
        if not agent_capabilities:
            raise AgentCapabilityViolationException("Agent has no capabilities assigned.")

        valid = False
        for cap_id in agent_capabilities:
            res = self.validate_capability(cap_id, tenant_id, required_scope, target_system)
            if res.is_valid:
                valid = True
                break

        if not valid:
            raise AgentCapabilityViolationException(
                f"Agent lacks capability for scope '{required_scope.value}' on target '{target_system or 'any'}'."
            )
        return True
