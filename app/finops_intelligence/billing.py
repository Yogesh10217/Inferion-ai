"""FinOps Intelligence Billing Integration (Phase 5.42)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from decimal import Decimal
import uuid
from pydantic import BaseModel, Field

from app.finops.cost_ledger import UnifiedCostLedger, CostCategory as PlatformCostCategory


class FinOpsCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"ev_fin_cost_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    component: str
    amount_usd: float
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FinOpsBillingTracker:
    """Delegates cost recording to UnifiedCostLedger without duplicating cost entries."""

    def __init__(self) -> None:
        self.cost_ledger = UnifiedCostLedger()
        self._events: List[FinOpsCostEvent] = []

    def record_cost_event(
        self,
        tenant_id: str,
        component: str,
        amount_usd: float,
        cost_category: PlatformCostCategory = PlatformCostCategory.COMPUTE,
    ) -> FinOpsCostEvent:
        event = FinOpsCostEvent(
            tenant_id=tenant_id,
            component=component,
            amount_usd=amount_usd,
        )
        self._events.append(event)

        # Delegate cost to UnifiedCostLedger
        self.cost_ledger.record_cost(
            component=component,
            cost_category=cost_category,
            quantity=Decimal("1.0"),
            unit_price=Decimal(str(amount_usd)),
            tenant_id=tenant_id,
            metadata={"finops_event_id": event.event_id},
        )
        return event

    def get_tenant_total_spend(self, tenant_id: str) -> float:
        return sum(e.amount_usd for e in self._events if e.tenant_id == tenant_id)
