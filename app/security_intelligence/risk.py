"""Security Risk Management Subsystem (Phase 5.32)."""

from typing import Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.governance_platform.risk import RiskManager, RiskCategory, RiskFactor, RiskSeverity, RiskAssessment


class SecurityRiskDimension(BaseModel):
    name: str
    risk_level: RiskSeverity = RiskSeverity.MEDIUM
    score: float = 50.0


class SecurityRiskProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: f"srp_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    overall_risk_level: RiskSeverity = RiskSeverity.HIGH
    dimensions: List[SecurityRiskDimension] = Field(default_factory=list)


class SecurityRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"sra_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    asset_id: str
    contract_risk: RiskAssessment
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityRiskManager:
    """Adapts and composes enterprise risk evaluation for security assets."""

    def __init__(self, enterprise_risk_manager: Optional[RiskManager] = None) -> None:
        self.enterprise_risk_manager = enterprise_risk_manager or RiskManager()

    def assess_security_risk(self, tenant_id: str, asset_id: str, threat_severity: str = "HIGH") -> SecurityRiskAssessment:
        factors = [RiskFactor(name="threat_severity", weight=1.0, impact_score=80.0 if threat_severity == "HIGH" else 40.0)]
        base_assessment = self.enterprise_risk_manager.calculate_risk(
            target_resource_id=asset_id,
            factors=factors,
            category=RiskCategory.SECURITY,
            tenant_id=tenant_id,
        )
        return SecurityRiskAssessment(
            tenant_id=tenant_id,
            asset_id=asset_id,
            contract_risk=base_assessment,
        )
