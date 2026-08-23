"""Enterprise Compliance Framework Registry & Management."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.compliance_platform.exceptions import (
    ComplianceFrameworkNotFoundException,
    CrossTenantComplianceAccessException,
)


class FrameworkType(str, Enum):
    CUSTOM = "CUSTOM"
    INTERNAL_POLICY = "INTERNAL_POLICY"
    ISO_27001 = "ISO_27001"
    SOC_2 = "SOC_2"
    GDPR = "GDPR"
    HIPAA = "HIPAA"
    PCI_DSS = "PCI_DSS"
    NIST_AI_RMF = "NIST_AI_RMF"
    NIST_CSF = "NIST_CSF"
    EU_AI_ACT = "EU_AI_ACT"
    INDUSTRY_SPECIFIC = "INDUSTRY_SPECIFIC"


class FrameworkStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    SUPERSEDED = "SUPERSEDED"


class RequirementCategory(str, Enum):
    GOVERNANCE = "GOVERNANCE"
    SECURITY = "SECURITY"
    PRIVACY = "PRIVACY"
    DATA = "DATA"
    MODEL = "MODEL"
    SAFETY = "SAFETY"
    TRANSPARENCY = "TRANSPARENCY"
    AUDIT = "AUDIT"


class FrameworkRequirement(BaseModel):
    requirement_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}")
    code: str  # e.g., NIST-GOVERN-1.1
    title: str
    description: str
    category: RequirementCategory = RequirementCategory.GOVERNANCE
    is_mandatory: bool = True


class ComplianceFrameworkVersion(BaseModel):
    version_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version_string: str = "1.0.0"
    description: str = "Initial Release"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComplianceFramework(BaseModel):
    framework_id: str = Field(default_factory=lambda: f"fw_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    framework_type: FrameworkType
    name: str
    description: str
    status: FrameworkStatus = FrameworkStatus.ACTIVE
    version: str = "1.0.0"
    requirements: List[FrameworkRequirement] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FrameworkManager:
    """Manages tenant-adopted compliance frameworks and requirement definitions."""

    def __init__(self) -> None:
        self._frameworks: Dict[str, ComplianceFramework] = {}

    def adopt_framework(
        self,
        tenant_id: str,
        framework_type: FrameworkType,
        name: str,
        description: str,
        requirements: Optional[List[FrameworkRequirement]] = None,
    ) -> ComplianceFramework:
        fw = ComplianceFramework(
            tenant_id=tenant_id,
            framework_type=framework_type,
            name=name,
            description=description,
            requirements=requirements or [],
        )
        self._frameworks[fw.framework_id] = fw
        return fw

    def get_framework(self, framework_id: str, tenant_id: str) -> ComplianceFramework:
        fw = self._frameworks.get(framework_id)
        if not fw:
            raise ComplianceFrameworkNotFoundException(framework_id=framework_id, tenant_id=tenant_id)
        if fw.tenant_id != tenant_id and tenant_id != "global" and fw.tenant_id != "global":
            raise CrossTenantComplianceAccessException(request_tenant=tenant_id, target_tenant=fw.tenant_id, resource_id=framework_id)
        return fw

    def list_frameworks(self, tenant_id: str) -> List[ComplianceFramework]:
        return [fw for fw in self._frameworks.values() if fw.tenant_id in (tenant_id, "global")]
