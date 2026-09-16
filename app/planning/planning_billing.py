"""
Planning Billing and Resource Usage Tracker
"""

import logging
import threading
from typing import Any, Dict

logger = logging.getLogger(__name__)


class PlanningBillingTracker:
    """Tracks compute usage, token usage, and billing cost for planning operations."""

    def __init__(self):
        self._lock = threading.RLock()
        self._tenant_billing: Dict[str, Dict[str, Any]] = {}

    def record_usage(
        self,
        tenant_id: str,
        operation: str,  # planning, reasoning, simulation, optimization
        cost: float,
        tokens_used: int = 0,
        compute_seconds: float = 0.0,
    ) -> Dict[str, Any]:
        with self._lock:
            if tenant_id not in self._tenant_billing:
                self._tenant_billing[tenant_id] = {
                    "tenant_id": tenant_id,
                    "total_cost": 0.0,
                    "tokens_used": 0,
                    "compute_seconds": 0.0,
                    "operation_counts": {},
                }

            b = self._tenant_billing[tenant_id]
            b["total_cost"] += cost
            b["tokens_used"] += tokens_used
            b["compute_seconds"] += compute_seconds
            op_counts = b["operation_counts"]
            op_counts[operation] = op_counts.get(operation, 0) + 1

            logger.debug(f"[PLANNING BILLING] Recorded {operation} for tenant '{tenant_id}' (cost=${cost:.4f})")
            return b

    def get_billing_summary(self, tenant_id: str) -> Dict[str, Any]:
        with self._lock:
            return self._tenant_billing.get(tenant_id, {
                "tenant_id": tenant_id,
                "total_cost": 0.0,
                "tokens_used": 0,
                "compute_seconds": 0.0,
                "operation_counts": {},
            })
