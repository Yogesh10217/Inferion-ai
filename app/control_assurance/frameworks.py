"""Control Framework Mapping Subsystem (Phase 5.38)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.control_assurance.exceptions import CrossTenantControlAssuranceAccessException
from app.platform_contracts.tenant import TenantAccessGuard


class FrameworkType(str, Enum):
    SECURITY = "SECURITY"
    PRIVACY = "PRIVACY"
    AI_GOVERNANCE = "AI_GOVERNANCE"
    FINANCIAL = "FINANCIAL"
    RELIABILITY = "RELIABILITY"
    CUSTOM = "CUSTOM"


class FrameworkVersion(BaseModel):
    version: str = "1.0.0"
    effective_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FrameworkRequirementReference(BaseModel):
    requirement_id: str
    code: str
    title: str
    external_compliance_ref: Optional[str] = None


class FrameworkControlMapping(BaseModel):
    mapping_id: str = Field(default_factory=lambda: f"map_{uuid.uuid4().hex[:12]}")
    framework_id: str
    control_id: str
    requirement_code: str
    coverage_weight: float = 1.0


class ControlFramework(BaseModel):
    framework_id: str = Field(default_factory=lambda: f"fw_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    code: str
    name: str
    description: str
    framework_type: FrameworkType = FrameworkType.SECURITY
    version: FrameworkVersion = Field(default_factory=FrameworkVersion)
    requirements: List[FrameworkRequirementReference] = Field(default_factory=list)
    mappings: List[FrameworkControlMapping] = Field(default_factory=list)
    is_active: bool = True


class ControlFrameworkManager:
    """Manages control framework mappings with tenant isolation."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._frameworks: Dict[str, ControlFramework] = {}

    def create_framework(
        self,
        tenant_id: str,
        code: str,
        name: str,
        description: str = "",
        framework_type: FrameworkType = FrameworkType.SECURITY,
        requirements: Optional[List[FrameworkRequirementReference]] = None,
    ) -> ControlFramework:
        fw = ControlFramework(
            tenant_id=tenant_id,
            code=code,
            name=name,
            description=description,
            framework_type=framework_type,
            requirements=requirements or [],
        )
        self._frameworks[fw.framework_id] = fw
        return fw

    def map_control_to_requirement(
        self,
        tenant_id: str,
        framework_id: str,
        control_id: str,
        requirement_code: str,
        coverage_weight: float = 1.0,
    ) -> FrameworkControlMapping:
        fw = self.get_framework(framework_id, tenant_id)
        mapping = FrameworkControlMapping(
            framework_id=framework_id,
            control_id=control_id,
            requirement_code=requirement_code,
            coverage_weight=coverage_weight,
        )
        fw.mappings.append(mapping)
        return mapping

    def get_framework(self, framework_id: str, tenant_id: str) -> ControlFramework:
        fw = self._frameworks.get(framework_id)
        if not fw:
            raise CrossTenantControlAssuranceAccessException()
        try:
            self.tenant_guard.enforce_isolation(tenant_id, fw.tenant_id)
        except Exception:
            raise CrossTenantControlAssuranceAccessException()
        return fw
