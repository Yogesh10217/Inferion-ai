"""Authorization Intelligence Layer."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class AuthorizationScope(BaseModel):
    scope_name: str
    resources_accessible: List[str] = Field(default_factory=list)
    permissions_granted: List[str] = Field(default_factory=list)


class AuthorizationContext(BaseModel):
    tenant_id: str
    requesting_identity_id: str
    target_resource_id: str
    requested_permission: str


class AuthorizationDecisionReference(BaseModel):
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    allowed: bool
    policy_evaluated: str = "default_policy"
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuthorizationAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    exposure_score: float = 0.2  # 0.0 to 1.0
    total_permissions: int = 10
    scopes: List[AuthorizationScope] = Field(default_factory=list)
    decision_risk: float = 0.1
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuthorizationIntelligenceManager:
    """Analyzes authorization scope, permission exposure, and decision risk."""

    def __init__(self) -> None:
        self._assessments: Dict[str, AuthorizationAssessment] = {}

    def assess_authorization(
        self,
        tenant_id: str,
        identity_id: str,
        permissions: Optional[List[str]] = None,
        resources: Optional[List[str]] = None,
    ) -> AuthorizationAssessment:
        perms = permissions or ["read:data", "write:reports"]
        res_list = resources or ["dataset-1", "report-1"]
        total_p = len(perms)
        exposure = min(1.0, total_p / 50.0)

        scope = AuthorizationScope(
            scope_name="standard_access",
            resources_accessible=res_list,
            permissions_granted=perms,
        )

        assessment = AuthorizationAssessment(
            identity_id=identity_id,
            tenant_id=tenant_id,
            exposure_score=exposure,
            total_permissions=total_p,
            scopes=[scope],
            decision_risk=0.1 if exposure < 0.5 else 0.4,
        )
        self._assessments[identity_id] = assessment
        return assessment

    def get_assessment(self, tenant_id: str, identity_id: str) -> AuthorizationAssessment:
        assessment = self._assessments.get(identity_id)
        if not assessment or assessment.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return assessment
