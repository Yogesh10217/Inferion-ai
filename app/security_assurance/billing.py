"""Security Billing & Cost Attribution Engine."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

from pydantic import BaseModel, Field

try:
    from app.finops.cost_ledger import UnifiedCostLedger
except ImportError:
    UnifiedCostLedger = None

logger = logging.getLogger(__name__)


class SecurityCostRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"cost-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    resource_id: str
    operation: str
    amount: float
    category: str = "SECURITY_ASSURANCE"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityBillingTracker:
    """Tracks financial cost and usage attribution for security assurance operations using UnifiedCostLedger."""

    def __init__(self) -> None:
        if UnifiedCostLedger is not None:
            try:
                self.cost_ledger = UnifiedCostLedger()
            except Exception:
                self.cost_ledger = None
        else:
            self.cost_ledger = None
        self._records: Dict[str, SecurityCostRecord] = {}

    def record_cost(self, tenant_id: str, resource_id: str, operation: str, amount: float = 0.05) -> Dict[str, Any]:
        rec = SecurityCostRecord(
            tenant_id=tenant_id,
            resource_id=resource_id,
            operation=operation,
            amount=amount,
        )
        self._records[rec.record_id] = rec
        if self.cost_ledger and hasattr(self.cost_ledger, "record_cost"):
            try:
                self.cost_ledger.record_entry(
                    tenant_id=tenant_id,
                    resource_id=resource_id,
                    amount=amount,
                    category="SECURITY_ASSURANCE",
                )
            except Exception as e:
                logger.debug(f"UnifiedCostLedger record_cost call skipped: {e}")

        logger.info(
            f"[SECURITY BILLING] Charged ${amount:.2f} to tenant '{tenant_id}' for operation '{operation}' on '{resource_id}'"
        )
        return rec.model_dump()
