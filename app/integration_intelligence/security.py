"""Integration Security Intelligence (Phase 5.40)."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import CrossTenantIntegrationAccessException


class IntegrationSecurityRisk(BaseModel):
    risk_id: str = Field(default_factory=lambda: f"sec_risk_{uuid.uuid4().hex[:8]}")
    category: str  # e.g., UNENCRYPTED_ENDPOINT, EXPOSED_CREDENTIAL_REF, WEAK_AUTH
    severity: str = "HIGH"
    description: str


class IntegrationSecurityAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"sec_asm_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_connector_id: str
    passed: bool = True
    risks: List[IntegrationSecurityRisk] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrationSecurityManager:
    """Composes with security_intelligence to evaluate integration security posture."""

    def __init__(self) -> None:
        self._assessments: Dict[str, IntegrationSecurityAssessment] = {}

    def evaluate_connector_security(
        self,
        tenant_id: str,
        connector_id: str,
        base_url: str,
        auth_type: str,
    ) -> IntegrationSecurityAssessment:
        risks: List[IntegrationSecurityRisk] = []
        if base_url.startswith("http://") and not base_url.startswith("http://localhost"):
            risks.append(IntegrationSecurityRisk(category="UNENCRYPTED_ENDPOINT", severity="HIGH", description="Endpoint uses unencrypted HTTP protocol."))
        if auth_type.upper() == "NONE":
            risks.append(IntegrationSecurityRisk(category="WEAK_AUTH", severity="CRITICAL", description="Connector configured with no authentication."))

        passed = len(risks) == 0
        asm = IntegrationSecurityAssessment(
            tenant_id=tenant_id,
            target_connector_id=connector_id,
            passed=passed,
            risks=risks,
        )
        self._assessments[asm.assessment_id] = asm
        return asm

    def get_assessment(self, tenant_id: str, assessment_id: str) -> IntegrationSecurityAssessment:
        asm = self._assessments.get(assessment_id)
        if not asm or asm.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return asm
