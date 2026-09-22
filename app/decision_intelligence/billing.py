"""Decision Intelligence Cost Attribution & Billing Tracker."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from app.finops.cost_ledger import UnifiedCostLedger


class DecisionCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"deccost_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    action: str  # SCENARIO_SIMULATION, RECOMMENDATION_GENERATION
    cost_usd: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionBillingTracker:
    """Tracks financial cost attribution for decision intelligence using UnifiedCostLedger."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()

    def record_activity_cost(self, tenant_id: str, action: str, amount_usd: float = 0.50) -> DecisionCostEvent:
        event = DecisionCostEvent(
            tenant_id=tenant_id,
            action=action,
            cost_usd=amount_usd,
        )
        self.cost_ledger.record_cost_event(
            tenant_id=tenant_id,
            service="decision_intelligence",
            action=action,
            cost_usd=amount_usd,
        )
        return event
