"""Platform Operations Cost Attribution & FinOps Tracking Engine."""

from datetime import datetime, timezone
from decimal import Decimal
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.finops.cost_ledger import UnifiedCostLedger, CostCategory

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PlatformOperationsCostEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"opcost_{uuid.uuid4().hex[:12]}")
    tenant_id: str = "global"
    service_id: str
    operation_type: str  # DIAGNOSIS, REMEDIATION, WORKFLOW_EXECUTION, SCALING, FALLBACK
    amount_usd: float
    timestamp: datetime = Field(default_factory=_now)


class PlatformOperationsBillingTracker:
    """Attributes operational activity costs into FinOps UnifiedCostLedger."""

    def __init__(self, cost_ledger: Optional[UnifiedCostLedger] = None) -> None:
        self.cost_ledger = cost_ledger or UnifiedCostLedger()
        self._events: List[PlatformOperationsCostEvent] = []

    def record_operation_cost(
        self,
        tenant_id: str,
        service_id: str,
        operation_type: str,
        amount_usd: float,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> PlatformOperationsCostEvent:
        evt = PlatformOperationsCostEvent(
            tenant_id=tenant_id,
            service_id=service_id,
            operation_type=operation_type,
            amount_usd=amount_usd,
        )
        self._events.append(evt)

        # Forward into FinOps UnifiedCostLedger
        self.cost_ledger.record_cost(
            component=f"platform_operations:{service_id}:{operation_type}",
            cost_category=CostCategory.OTHER,
            quantity=Decimal("1.0"),
            unit_price=Decimal(str(amount_usd)),
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            project_id=project_id,
            resource_id=service_id,
            metadata={"operation_type": operation_type, "service_id": service_id},
        )
        logger.info(f"[PLATFORM OPERATIONS BILLING] Attributed ${amount_usd:.4f} for operation '{operation_type}' on service '{service_id}'")
        return evt
