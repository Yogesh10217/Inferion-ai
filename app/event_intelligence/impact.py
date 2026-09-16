"""Enterprise Impact Analysis Subsystem (Phase 5.34)."""

import uuid
from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field

from app.event_intelligence.events import EnterpriseEvent, EventSeverity


class EventImpactSeverity(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class BusinessImpact(BaseModel):
    severity: EventImpactSeverity = EventImpactSeverity.MEDIUM
    score: float = 50.0


class TechnicalImpact(BaseModel):
    severity: EventImpactSeverity = EventImpactSeverity.MEDIUM
    impacted_services_count: int = 1


class FinancialImpact(BaseModel):
    estimated_cost_usd: float = 0.0


class ComplianceImpact(BaseModel):
    violates_compliance: bool = False


class CustomerImpact(BaseModel):
    affected_users: int = 0


class EventImpactDimension(BaseModel):
    dimension_name: str
    impact_level: EventImpactSeverity = EventImpactSeverity.MEDIUM


class EventImpactAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"imp_{uuid.uuid4().hex[:12]}")
    event_id: str
    tenant_id: str
    overall_severity: EventImpactSeverity = EventImpactSeverity.MEDIUM
    business: BusinessImpact = Field(default_factory=BusinessImpact)
    technical: TechnicalImpact = Field(default_factory=TechnicalImpact)
    financial: FinancialImpact = Field(default_factory=FinancialImpact)
    compliance: ComplianceImpact = Field(default_factory=ComplianceImpact)
    customer: CustomerImpact = Field(default_factory=CustomerImpact)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EventImpactAnalyzer:
    """Analyzes multi-dimensional enterprise impact for events."""

    def analyze_impact(self, event: EnterpriseEvent) -> EventImpactAssessment:
        sev = EventImpactSeverity.MEDIUM
        if event.severity == EventSeverity.CRITICAL:
            sev = EventImpactSeverity.CRITICAL
        elif event.severity == EventSeverity.HIGH:
            sev = EventImpactSeverity.HIGH
        elif event.severity == EventSeverity.LOW:
            sev = EventImpactSeverity.LOW

        return EventImpactAssessment(
            event_id=event.event_id,
            tenant_id=event.tenant_id,
            overall_severity=sev,
            business=BusinessImpact(severity=sev, score=80.0 if sev in (EventImpactSeverity.HIGH, EventImpactSeverity.CRITICAL) else 30.0),
            technical=TechnicalImpact(severity=sev, impacted_services_count=3 if sev == EventImpactSeverity.CRITICAL else 1),
            financial=FinancialImpact(estimated_cost_usd=500.0 if sev == EventImpactSeverity.CRITICAL else 0.0),
        )
