"""Event Classification Subsystem (Phase 5.34)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.event_intelligence.events import EnterpriseEvent, EventSeverity, EventCategory


class ClassificationConfidence(BaseModel):
    score: float = 0.95


class EventClassificationDimension(BaseModel):
    name: str
    value: str


class EventClassification(BaseModel):
    classification_id: str = Field(default_factory=lambda: f"cls_{uuid.uuid4().hex[:12]}")
    event_id: str
    tenant_id: str
    domain: EventCategory
    business_impact: str = "MEDIUM"
    technical_impact: str = "MEDIUM"
    urgency: str = "MEDIUM"
    automation_eligible: bool = True
    governance_sensitive: bool = False
    confidence: ClassificationConfidence = Field(default_factory=ClassificationConfidence)


class EventClassifier:
    """Classifies enterprise events across impact, domain, urgency, and governance dimensions."""

    def classify_event(self, event: EnterpriseEvent) -> EventClassification:
        is_gov_sensitive = event.category in (
            EventCategory.SECURITY,
            EventCategory.COMPLIANCE,
            EventCategory.FINANCIAL,
            EventCategory.DATA_GOVERNANCE,
        ) or event.severity in (EventSeverity.HIGH, EventSeverity.CRITICAL)

        b_impact = "HIGH" if event.severity in (EventSeverity.HIGH, EventSeverity.CRITICAL) else "MEDIUM"
        t_impact = "HIGH" if event.severity == EventSeverity.CRITICAL else "MEDIUM"
        urg = "HIGH" if event.severity in (EventSeverity.HIGH, EventSeverity.CRITICAL) else "LOW"

        return EventClassification(
            event_id=event.event_id,
            tenant_id=event.tenant_id,
            domain=event.category,
            business_impact=b_impact,
            technical_impact=t_impact,
            urgency=urg,
            automation_eligible=True,
            governance_sensitive=is_gov_sensitive,
        )
