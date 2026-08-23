"""Portfolio Cost Attribution & Billing Tracker."""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.finops.cost_ledger import UnifiedCostLedger


class PortfolioCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"cost_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    action: str  # PORTFOLIO_OPTIMIZATION, BUSINESS_CASE_EVALUATION
    cost_usd: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PortfolioBillingTracker:
    """Tracks financial cost attribution for portfolio activities using UnifiedCostLedger."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()

    def record_activity_cost(self, tenant_id: str, action: str, amount_usd: float = 1.00) -> PortfolioCostEvent:
        event = PortfolioCostEvent(
            tenant_id=tenant_id,
            action=action,
            cost_usd=amount_usd,
        )
        self.cost_ledger.record_cost(
            tenant_id=tenant_id,
            service="portfolio_platform",
            action=action,
            cost_usd=amount_usd,
        )
        return event
