"""Event Prioritization Subsystem (Phase 5.34)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.event_intelligence.events import EnterpriseEvent, EventSeverity, EventPriority


class PriorityDimension(BaseModel):
    name: str
    score: float = 50.0


class EventPriorityScore(BaseModel):
    overall_score: float = 75.0
    dimensions: List[PriorityDimension] = Field(default_factory=list)


class EventPrioritizationResult(BaseModel):
    event_id: str
    tenant_id: str
    priority: EventPriority = EventPriority.P3_MEDIUM
    score: EventPriorityScore = Field(default_factory=EventPriorityScore)


class EventPrioritizationEngine:
    """Prioritizes enterprise events using hard constraints and multi-dimensional scoring."""

    def prioritize_event(
        self,
        event: EnterpriseEvent,
        security_risk_high: bool = False,
        business_impact_high: bool = False,
    ) -> EventPrioritizationResult:
        # Hard constraint override
        if event.severity == EventSeverity.CRITICAL or (security_risk_high and business_impact_high):
            prio = EventPriority.P1_CRITICAL
            score_val = 98.0
        elif event.severity == EventSeverity.HIGH or security_risk_high:
            prio = EventPriority.P2_HIGH
            score_val = 85.0
        elif event.severity == EventSeverity.MEDIUM:
            prio = EventPriority.P3_MEDIUM
            score_val = 50.0
        else:
            prio = EventPriority.P4_LOW
            score_val = 20.0

        dims = [
            PriorityDimension(name="severity", score=score_val),
            PriorityDimension(name="security_risk", score=90.0 if security_risk_high else 30.0),
            PriorityDimension(name="business_impact", score=90.0 if business_impact_high else 30.0),
        ]
        return EventPrioritizationResult(
            event_id=event.event_id,
            tenant_id=event.tenant_id,
            priority=prio,
            score=EventPriorityScore(overall_score=score_val, dimensions=dims),
        )
