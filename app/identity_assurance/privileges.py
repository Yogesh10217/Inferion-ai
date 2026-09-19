"""Privilege Risk Intelligence."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class PrivilegeType(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    ADMIN = "ADMIN"
    EXECUTE = "EXECUTE"
    DELEGATE = "DELEGATE"
    SYSTEM = "SYSTEM"


class PrivilegeScope(BaseModel):
    scope_name: str = "default_scope"
    target_resource_pattern: str = "*"


class PrivilegeRisk(BaseModel):
    risk_score: float = 0.1  # 0.0 to 1.0
    is_excessive: bool = False
    is_concentrated: bool = False
    has_creep: bool = False
    risk_factors: List[str] = Field(default_factory=list)


class PrivilegeReference(BaseModel):
    privilege_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    privilege_type: PrivilegeType
    scope: PrivilegeScope = Field(default_factory=PrivilegeScope)
    is_sensitive: bool = False


class PrivilegeAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    privileges: List[PrivilegeReference] = Field(default_factory=list)
    risk: PrivilegeRisk = Field(default_factory=PrivilegeRisk)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PrivilegeIntelligenceManager:
    """Detects privilege risk, excessive privileges, and concentration."""

    def __init__(self) -> None:
        self._assessments: Dict[str, PrivilegeAssessment] = {}

    def assess_privileges(
        self,
        tenant_id: str,
        identity_id: str,
        privileges: Optional[List[PrivilegeReference]] = None,
    ) -> PrivilegeAssessment:
        priv_list = privileges or [PrivilegeReference(name="data:read", privilege_type=PrivilegeType.READ)]
        has_admin = any(p.privilege_type == PrivilegeType.ADMIN for p in priv_list)
        excessive = len(priv_list) > 20 or (has_admin and len(priv_list) > 10)
        concentrated = len([p for p in priv_list if p.is_sensitive]) > 3

        risk_score = 0.8 if (has_admin and excessive) else (0.4 if has_admin else 0.1)

        factors = []
        if has_admin:
            factors.append("Administrative privileges assigned")
        if excessive:
            factors.append("Excessive privilege count")
        if concentrated:
            factors.append("High sensitive privilege concentration")

        risk = PrivilegeRisk(
            risk_score=risk_score,
            is_excessive=excessive,
            is_concentrated=concentrated,
            has_creep=False,
            risk_factors=factors,
        )

        assessment = PrivilegeAssessment(
            identity_id=identity_id,
            tenant_id=tenant_id,
            privileges=priv_list,
            risk=risk,
        )
        self._assessments[identity_id] = assessment
        return assessment

    def get_assessment(self, tenant_id: str, identity_id: str) -> PrivilegeAssessment:
        assessment = self._assessments.get(identity_id)
        if not assessment or assessment.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return assessment
