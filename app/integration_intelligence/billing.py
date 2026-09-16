"""Integration Billing & Cost Attribution (Phase 5.40)."""

import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import List

from pydantic import BaseModel, Field

from app.finops.cost_ledger import CostCategory, UnifiedCostLedger


class IntegrationCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"cost_int_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    workflow_id: str
    action_type: str  # WORKFLOW_EXECUTION, CONNECTOR_CALL, RETRY, RECOVERY_OPERATION
    estimated_cost_usd: float = 0.001
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrationBillingTracker:
    """Delegates cost tracking to UnifiedCostLedger for integration operations."""

    def __init__(self) -> None:
        self.cost_ledger = UnifiedCostLedger()
        self._events: List[IntegrationCostEvent] = []

    def record_cost(
        self,
        tenant_id: str,
        workflow_id: str,
        action_type: str,
        amount_usd: float = 0.001,
    ) -> IntegrationCostEvent:
        event = IntegrationCostEvent(
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            action_type=action_type,
            estimated_cost_usd=amount_usd,
        )
        self._events.append(event)

        # Delegate cost to UnifiedCostLedger
        self.cost_ledger.record_cost(
            component="INTEGRATION",
            cost_category=CostCategory.WORKFLOW_EXECUTION,
            quantity=Decimal("1.0"),
            unit_price=Decimal(str(amount_usd)),
            tenant_id=tenant_id,
            resource_id=workflow_id,
            metadata={"action_type": action_type},
        )
        return event

    def get_tenant_cost(self, tenant_id: str) -> float:
        events = [e for e in self._events if e.tenant_id == tenant_id]
        return sum(e.estimated_cost_usd for e in events)
