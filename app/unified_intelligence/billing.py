"""
Intelligence Usage Billing Engine for Phase 5.51 Enterprise AI Unified Intelligence.

Tracks tenant resource consumption, signal ingestion units, situation processing credits,
and cross-domain reasoning metrics for accurate billing and quota enforcement.
"""

from typing import Dict, Any, Optional
from datetime import datetime

from app.unified_intelligence.exceptions import (
    InvalidUnifiedIntelligenceInputException
)


class UnifiedBillingRecord:
    """
    Billing consumption snapshot for a tenant.
    """
    def __init__(
        self,
        tenant_id: str,
        signals_processed: int,
        situations_evaluated: int,
        correlations_computed: int,
        total_billing_units: float,
        billing_period: str,  # e.g., '2026-09'
        updated_at: Optional[datetime] = None
    ):
        self.tenant_id = tenant_id
        self.signals_processed = signals_processed
        self.situations_evaluated = situations_evaluated
        self.correlations_computed = correlations_computed
        self.total_billing_units = total_billing_units
        self.billing_period = billing_period
        self.updated_at = updated_at or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tenant_id": self.tenant_id,
            "signals_processed": self.signals_processed,
            "situations_evaluated": self.situations_evaluated,
            "correlations_computed": self.correlations_computed,
            "total_billing_units": round(self.total_billing_units, 4),
            "billing_period": self.billing_period,
            "updated_at": self.updated_at.isoformat()
        }


class IntelligenceBillingEngine:
    """
    Manages tenant usage metering for cross-domain intelligence operations.
    """
    def __init__(self):
        self._tenant_usage: Dict[str, UnifiedBillingRecord] = {}

    def record_usage(
        self,
        tenant_id: str,
        signals: int = 1,
        situations: int = 0,
        correlations: int = 0
    ) -> UnifiedBillingRecord:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")

        period = datetime.utcnow().strftime("%Y-%m")
        key = f"{tenant_id}:{period}"

        record = self._tenant_usage.get(key)
        if not record:
            record = UnifiedBillingRecord(
                tenant_id=tenant_id,
                signals_processed=0,
                situations_evaluated=0,
                correlations_computed=0,
                total_billing_units=0.0,
                billing_period=period
            )
            self._tenant_usage[key] = record

        record.signals_processed += signals
        record.situations_evaluated += situations
        record.correlations_computed += correlations
        # Calculation: 0.01 per signal + 0.10 per situation + 0.05 per correlation
        record.total_billing_units = (
            (record.signals_processed * 0.01)
            + (record.situations_evaluated * 0.10)
            + (record.correlations_computed * 0.05)
        )
        record.updated_at = datetime.utcnow()
        return record

    def get_tenant_billing(self, tenant_id: str) -> UnifiedBillingRecord:
        if not tenant_id:
            raise InvalidUnifiedIntelligenceInputException("tenant_id is required")
        period = datetime.utcnow().strftime("%Y-%m")
        key = f"{tenant_id}:{period}"
        return self._tenant_usage.get(
            key,
            UnifiedBillingRecord(tenant_id=tenant_id, signals_processed=0, situations_evaluated=0, correlations_computed=0, total_billing_units=0.0, billing_period=period)
        )
