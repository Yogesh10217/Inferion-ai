"""Continuous Identity Profile Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException
from app.identity_assurance.identities import IdentityReference


class IdentityAttribute(BaseModel):
    key: str
    value: Any
    category: str = "standard"


class IdentityCapability(BaseModel):
    capability_name: str
    granted_by: str = "role"
    risk_level: str = "LOW"


class IdentityContext(BaseModel):
    tenant_id: str
    environment: str = "production"
    business_unit: str = "engineering"
    security_clearance: str = "STANDARD"


class IdentityProfileAssessment(BaseModel):
    profile_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    purpose: str = "Enterprise Access"
    ownership: str = "System"
    environment: str = "production"
    criticality: str = "MEDIUM"  # LOW, MEDIUM, HIGH, CRITICAL
    access_scope: str = "STANDARD"
    trust_posture: float = 0.85
    attributes: List[IdentityAttribute] = Field(default_factory=list)
    capabilities: List[IdentityCapability] = Field(default_factory=list)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityProfileManager:
    """Manages continuous identity profile assessments."""

    def __init__(self) -> None:
        self._profiles: Dict[str, IdentityProfileAssessment] = {}

    def assess_profile(
        self,
        tenant_id: str,
        identity: IdentityReference,
        criticality: str = "MEDIUM",
        access_scope: str = "STANDARD",
    ) -> IdentityProfileAssessment:
        profile = IdentityProfileAssessment(
            identity_id=identity.identity_id,
            tenant_id=tenant_id,
            purpose=f"Access profile for {identity.name}",
            ownership=identity.metadata.owner,
            environment=identity.metadata.environment,
            criticality=criticality,
            access_scope=access_scope,
            trust_posture=0.90 if identity.status == "ACTIVE" else 0.40,
        )
        self._profiles[identity.identity_id] = profile
        return profile

    def get_profile(self, tenant_id: str, identity_id: str) -> IdentityProfileAssessment:
        profile = self._profiles.get(identity_id)
        if not profile or profile.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return profile
