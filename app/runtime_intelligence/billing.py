"""FinOps cost tracking integration for Runtime Intelligence (Phase 5.57)."""

import logging
import threading
from typing import Dict, Any

logger = logging.getLogger(__name__)


class RuntimeIntelligenceBillingTracker:
    """Tracks FinOps usage for signal processing, correlation, analysis, and snapshots with tenant isolation."""

    RATES_PER_UNIT = {
        "SIGNAL_INGESTION": 0.0001,
        "HEALTH_EVALUATION": 0.0005,
        "ANOMALY_DETECTION": 0.0010,
        "SNAPSHOT_CAPTURE": 0.0020,
        "EVIDENCE_SEALING": 0.0015,
        "DEFAULT": 0.0005,
    }

    def __init__(self) -> None:
        self._usage: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()

    def record_usage(self, tenant_id: str, operation_type: str, units: int = 1) -> Dict[str, Any]:
        rate = self.RATES_PER_UNIT.get(operation_type.upper(), self.RATES_PER_UNIT["DEFAULT"])
        cost = round(units * rate, 6)

        with self._lock:
            if tenant_id not in self._usage:
                self._usage[tenant_id] = {"total_operations": 0, "total_cost_usd": 0.0, "by_operation": {}}

            t_usage = self._usage[tenant_id]
            t_usage["total_operations"] += units
            t_usage["total_cost_usd"] = round(t_usage["total_cost_usd"] + cost, 6)

            if operation_type not in t_usage["by_operation"]:
                t_usage["by_operation"][operation_type] = {"units": 0, "cost_usd": 0.0}
            t_usage["by_operation"][operation_type]["units"] += units
            t_usage["by_operation"][operation_type]["cost_usd"] = round(
                t_usage["by_operation"][operation_type]["cost_usd"] + cost, 6
            )

        logger.debug(f"Tracked Runtime FinOps billing for '{tenant_id}' ({operation_type}): ${cost:.6f}")
        return {"tenant_id": tenant_id, "operation_type": operation_type, "units": units, "cost_usd": cost}

    def get_usage_summary(self, tenant_id: str) -> Dict[str, Any]:
        with self._lock:
            t_usage = self._usage.get(tenant_id)
            if not t_usage:
                return {"tenant_id": tenant_id, "total_operations": 0, "total_cost_usd": 0.0, "by_operation": {}}
            return {
                "tenant_id": tenant_id,
                "total_operations": t_usage["total_operations"],
                "total_cost_usd": round(t_usage["total_cost_usd"], 4),
                "by_operation": t_usage["by_operation"],
            }
