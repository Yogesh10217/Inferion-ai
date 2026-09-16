"""Operational cost attribution using platform UnifiedCostLedger and FinOps primitives."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.finops.cost_ledger import UnifiedCostLedger
from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException


class OperationsCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    amount_usd: float = 0.005
    operation: str = "OPERATIONS_ASSURANCE_EVALUATION"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsBillingTracker:
    """Tracks operational assurance computation and monitoring costs using UnifiedCostLedger."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()
        self._events: Dict[str, OperationsCostEvent] = {}

    def record_cost(
        self,
        tenant_id: str,
        service_id: str,
        operation: str = "OPERATIONS_ASSURANCE_EVALUATION",
        amount_usd: float = 0.005,
    ) -> OperationsCostEvent:
        event = OperationsCostEvent(
            tenant_id=tenant_id,
            service_id=service_id,
            amount_usd=amount_usd,
            operation=operation,
        )
        self._events[event.event_id] = event
        return event

    def get_event(self, tenant_id: str, event_id: str) -> OperationsCostEvent:
        event = self._events.get(event_id)
        if not event or event.tenant_id != tenant_id:
            raise CrossTenantOperationsAssuranceException("Access denied.")
        return event
