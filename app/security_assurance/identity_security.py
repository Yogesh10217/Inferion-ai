"""Identity Security Intelligence Engine."""

from typing import Dict, Any, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class IdentityRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"idsec-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    identity_id: str
    excessive_permissions_count: int = 0
    mfa_enabled: bool = True
    risk_score: float = 0.0
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentitySecurityEngine:
    """Evaluates security risks associated with human and workload identities."""

    def assess_identity_security(self, tenant_id: str, identity_id: str, excessive_permissions: int = 0, mfa_enabled: bool = True) -> IdentityRiskAssessment:
        score = (excessive_permissions * 2.0) + (0.0 if mfa_enabled else 5.0)
        return IdentityRiskAssessment(
            tenant_id=tenant_id,
            identity_id=identity_id,
            excessive_permissions_count=excessive_permissions,
            mfa_enabled=mfa_enabled,
            risk_score=min(10.0, score),
        )
