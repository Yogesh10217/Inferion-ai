"""Requirement Applicability & Governance Evaluation Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.compliance_platform.exceptions import (
    ComplianceRequirementNotFoundException,
    CrossTenantComplianceAccessException,
)


class RequirementStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    DRAFT = "DRAFT"


class RequirementPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RequirementScope(str, Enum):
    APPLICATION = "APPLICATION"
    MODEL = "MODEL"
    AGENT = "AGENT"
    WORKFLOW = "WORKFLOW"
    DATA_ASSET = "DATA_ASSET"
    ARCHITECTURE_NODE = "ARCHITECTURE_NODE"
    SERVICE = "SERVICE"
    INTEGRATION = "INTEGRATION"
    TENANT = "TENANT"
    ORGANIZATION = "ORGANIZATION"


class RequirementApplicabilityState(str, Enum):
    APPLICABLE = "APPLICABLE"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"
    REQUIRES_REVIEW = "REQUIRES_REVIEW"


class ComplianceRequirement(BaseModel):
    requirement_id: str = Field(default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    framework_id: str
    code: str
    title: str
    description: str
    scope: RequirementScope = RequirementScope.TENANT
    priority: RequirementPriority = RequirementPriority.HIGH
    status: RequirementStatus = RequirementStatus.ACTIVE
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RequirementApplicabilityDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"appdec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    requirement_id: str
    subject_type: RequirementScope
    subject_id: str
    applicability: RequirementApplicabilityState
    reason: str
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RequirementManager:
    """Manages compliance requirements and evaluates context-specific applicability."""

    def __init__(self) -> None:
        self._requirements: Dict[str, ComplianceRequirement] = {}

    def register_requirement(
        self,
        tenant_id: str,
        framework_id: str,
        code: str,
        title: str,
        description: str,
        scope: RequirementScope = RequirementScope.TENANT,
        priority: RequirementPriority = RequirementPriority.HIGH,
    ) -> ComplianceRequirement:
        req = ComplianceRequirement(
            tenant_id=tenant_id,
            framework_id=framework_id,
            code=code,
            title=title,
            description=description,
            scope=scope,
            priority=priority,
        )
        self._requirements[req.requirement_id] = req
        return req

    def get_requirement(self, requirement_id: str, tenant_id: str) -> ComplianceRequirement:
        req = self._requirements.get(requirement_id)
        if not req:
            raise ComplianceRequirementNotFoundException(requirement_id=requirement_id, tenant_id=tenant_id)
        if req.tenant_id != tenant_id and tenant_id != "global" and req.tenant_id != "global":
            raise CrossTenantComplianceAccessException(request_tenant=tenant_id, target_tenant=req.tenant_id, resource_id=requirement_id)
        return req

    def list_requirements(self, tenant_id: str, framework_id: Optional[str] = None) -> List[ComplianceRequirement]:
        reqs = [r for r in self._requirements.values() if r.tenant_id in (tenant_id, "global")]
        if framework_id:
            reqs = [r for r in reqs if r.framework_id == framework_id]
        return reqs

    def evaluate_applicability(
        self,
        tenant_id: str,
        requirement_id: str,
        subject_type: RequirementScope,
        subject_id: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> RequirementApplicabilityDecision:
        req = self.get_requirement(requirement_id, tenant_id)
        attrs = attributes or {}

        if req.scope == RequirementScope.TENANT or req.scope == subject_type:
            state = RequirementApplicabilityState.APPLICABLE
            reason = f"Requirement '{req.code}' directly applies to scope {subject_type.value}."
        elif attrs.get("is_exempt", False):
            state = RequirementApplicabilityState.NOT_APPLICABLE
            reason = f"Subject '{subject_id}' has documented exemption for requirement '{req.code}'."
        else:
            state = RequirementApplicabilityState.APPLICABLE
            reason = f"Evaluated applicability for requirement '{req.code}'."

        return RequirementApplicabilityDecision(
            tenant_id=tenant_id,
            requirement_id=requirement_id,
            subject_type=subject_type,
            subject_id=subject_id,
            applicability=state,
            reason=reason,
        )
