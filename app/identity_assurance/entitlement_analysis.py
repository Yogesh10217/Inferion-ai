"""Enterprise Entitlement Analysis Intelligence."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class EntitlementType(str, Enum):
    ROLE = "ROLE"
    PERMISSION = "PERMISSION"
    GROUP = "GROUP"
    DIRECT = "DIRECT"
    DELEGATED = "DELEGATED"


class EntitlementReference(BaseModel):
    entitlement_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role_name: str
    permission: str
    resource_id: str
    entitlement_type: EntitlementType = EntitlementType.ROLE


class EntitlementRisk(BaseModel):
    risk_level: str = "LOW"
    unused_entitlements_count: int = 0
    risk_score: float = 0.1


class EntitlementAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    entitlements: List[EntitlementReference] = Field(default_factory=list)
    risk: EntitlementRisk = Field(default_factory=EntitlementRisk)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EntitlementAnalysisManager:
    """Analyzes Identity -> Role -> Permission -> Resource relationships."""

    def __init__(self) -> None:
        self._assessments: Dict[str, EntitlementAssessment] = {}

    def analyze_entitlements(
        self,
        tenant_id: str,
        identity_id: str,
        entitlements: Optional[List[EntitlementReference]] = None,
    ) -> EntitlementAssessment:
        ent_list = entitlements or [
            EntitlementReference(role_name="Developer", permission="code:read", resource_id="repo-1")
        ]
        risk = EntitlementRisk(
            risk_level="LOW" if len(ent_list) <= 5 else "MEDIUM",
            unused_entitlements_count=max(0, len(ent_list) - 2),
            risk_score=min(1.0, len(ent_list) * 0.05),
        )
        assessment = EntitlementAssessment(
            identity_id=identity_id,
            tenant_id=tenant_id,
            entitlements=ent_list,
            risk=risk,
        )
        self._assessments[identity_id] = assessment
        return assessment

    def get_assessment(self, tenant_id: str, identity_id: str) -> EntitlementAssessment:
        assessment = self._assessments.get(identity_id)
        if not assessment or assessment.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return assessment
