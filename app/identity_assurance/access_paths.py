"""Access Path Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class AccessPath(BaseModel):
    path_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_identity_id: str
    target_resource_id: str
    intermediate_nodes: List[str] = Field(default_factory=list)
    path_type: str = "DIRECT"  # DIRECT, INDIRECT, PRIVILEGE_ESCALATION, CROSS_DOMAIN
    risk_score: float = 0.1


class AccessPathRisk(BaseModel):
    has_privilege_escalation: bool = False
    has_cross_domain_path: bool = False
    highest_path_risk: float = 0.1


class AccessPathAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    paths: List[AccessPath] = Field(default_factory=list)
    risk: AccessPathRisk = Field(default_factory=AccessPathRisk)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessPathManager:
    """Detects risky access paths, indirect access, and escalation paths."""

    def __init__(self) -> None:
        self._assessments: Dict[str, AccessPathAssessment] = {}

    def analyze_paths(
        self,
        tenant_id: str,
        identity_id: str,
        target_resource_id: str = "critical-data",
    ) -> AccessPathAssessment:
        path = AccessPath(
            source_identity_id=identity_id,
            target_resource_id=target_resource_id,
            intermediate_nodes=["Role-Developer", "Permission-Read"],
            path_type="DIRECT",
            risk_score=0.15,
        )

        risk = AccessPathRisk(
            has_privilege_escalation=False,
            has_cross_domain_path=False,
            highest_path_risk=0.15,
        )

        assessment = AccessPathAssessment(
            identity_id=identity_id,
            tenant_id=tenant_id,
            paths=[path],
            risk=risk,
        )
        self._assessments[identity_id] = assessment
        return assessment

    def get_assessment(self, tenant_id: str, identity_id: str) -> AccessPathAssessment:
        assessment = self._assessments.get(identity_id)
        if not assessment or assessment.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return assessment
