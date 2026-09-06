"""Identity Assurance Billing & Cost Attribution."""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
import uuid
from pydantic import BaseModel, Field

from app.finops.cost_ledger import UnifiedCostLedger
from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class IdentityAssuranceCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    identity_id: str
    amount_usd: float = 0.001
    operation: str = "IDENTITY_ASSURANCE_EVALUATION"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IdentityAssuranceBillingTracker:
    """Tracks identity assurance evaluation costs using platform UnifiedCostLedger."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()
        self._events: Dict[str, IdentityAssuranceCostEvent] = {}

    def record_cost(
        self,
        tenant_id: str,
        identity_id: str,
        operation: str = "IDENTITY_ASSURANCE_EVALUATION",
        amount_usd: float = 0.001,
    ) -> IdentityAssuranceCostEvent:
        event = IdentityAssuranceCostEvent(
            tenant_id=tenant_id,
            identity_id=identity_id,
            amount_usd=amount_usd,
            operation=operation,
        )
        self._events[event.event_id] = event
        return event

    def get_event(self, tenant_id: str, event_id: str) -> IdentityAssuranceCostEvent:
        event = self._events.get(event_id)
        if not event or event.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return event
