"""Compliance Cost Attribution & Billing Tracker."""

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field

from app.finops.cost_ledger import UnifiedCostLedger


class ComplianceCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"cost_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    action: str  # EVIDENCE_COLLECTION, COMPLIANCE_ASSESSMENT, ASSURANCE_REPORT
    cost_usd: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComplianceBillingTracker:
    """Tracks financial cost attribution for compliance activities using UnifiedCostLedger."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()

    def record_activity_cost(self, tenant_id: str, action: str, amount_usd: float = 0.50) -> ComplianceCostEvent:
        event = ComplianceCostEvent(
            tenant_id=tenant_id,
            action=action,
            cost_usd=amount_usd,
        )
        self.cost_ledger.record_cost_event(
            tenant_id=tenant_id,
            service="compliance_platform",
            action=action,
            cost_usd=amount_usd,
        )
        return event
