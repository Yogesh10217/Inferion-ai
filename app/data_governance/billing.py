"""Financial Cost Attribution wrapping UnifiedCostLedger for Data Governance."""

from datetime import datetime, timezone
import uuid
import logging
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from app.finops.cost_ledger import UnifiedCostLedger

logger = logging.getLogger(__name__)


class DataGovernanceCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"gov_cost_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    operation_type: str  # CLASSIFICATION, QUALITY_VALIDATION, LINEAGE_PROCESSING, STORAGE_LIFECYCLE, PRIVACY_OPERATIONS, DATA_SHARING
    amount_usd: float = 0.002
    resource_id: Optional[str] = None
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataGovernanceBillingTracker:
    """Attributes Data Governance cost events to UnifiedCostLedger."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()
        self._events: Dict[str, DataGovernanceCostEvent] = {}

    def record_cost(
        self,
        tenant_id: str,
        operation_type: str,
        amount_usd: float = 0.002,
        resource_id: Optional[str] = None,
    ) -> DataGovernanceCostEvent:
        event = DataGovernanceCostEvent(
            tenant_id=tenant_id,
            operation_type=operation_type,
            amount_usd=amount_usd,
            resource_id=resource_id,
        )
        self._events[event.event_id] = event

        # Record to FinOps ledger if available
        try:
            self.cost_ledger.record_entry(
                tenant_id=tenant_id,
                resource_id=resource_id or "governance",
                resource_type="DATA_GOVERNANCE",
                amount=amount_usd,
                metadata={"operation_type": operation_type},
            )
        except Exception as exc:
            logger.debug(f"Recorded governance cost locally: {exc}")

        return event
