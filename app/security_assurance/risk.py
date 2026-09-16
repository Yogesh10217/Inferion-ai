"""Security Risk Assessment Engine."""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, Field


class SecurityRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"sec-risk-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    risk_score: float  # 0.0 to 100.0
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    threats_factor: float
    vulnerabilities_factor: float
    misconfigurations_factor: float
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityRiskEngine:
    """Evaluates comprehensive enterprise security risk score for a tenant."""

    def calculate_enterprise_security_risk(
        self,
        tenant_id: str,
        threats_count: int = 0,
        vulns_count: int = 0,
        misconfigs_count: int = 0,
    ) -> SecurityRiskAssessment:
        t_factor = threats_count * 15.0
        v_factor = vulns_count * 5.0
        m_factor = misconfigs_count * 3.0

        total_risk = min(100.0, t_factor + v_factor + m_factor)

        if total_risk >= 75.0:
            level = "CRITICAL"
        elif total_risk >= 50.0:
            level = "HIGH"
        elif total_risk >= 25.0:
            level = "MEDIUM"
        else:
            level = "LOW"

        return SecurityRiskAssessment(
            tenant_id=tenant_id,
            risk_score=round(total_risk, 2),
            risk_level=level,
            threats_factor=t_factor,
            vulnerabilities_factor=v_factor,
            misconfigurations_factor=m_factor,
        )
