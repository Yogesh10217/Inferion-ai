"""Runtime Objective Engine for Phase 5.57 Runtime Intelligence."""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


@dataclass
class RuntimeObjectiveEvaluation:
    evaluation_id: str
    tenant_id: str
    target_service_id: str
    objective_name: str  # LATENCY_TARGET, ERROR_RATE_TARGET, THROUGHPUT_TARGET, AVAILABILITY_TARGET, COST_TARGET
    target_value: float
    actual_value: float
    is_met: bool
    evaluated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class RuntimeObjectiveEngine:
    """Evaluates service-level objectives (SLOs) against actual runtime metrics."""

    def evaluate_objective(
        self, tenant_id: str, target_service_id: str, objective_name: str, target_value: float, actual_value: float
    ) -> RuntimeObjectiveEvaluation:
        # For latency/error/cost, lower is better. For throughput/availability, higher is better.
        if objective_name.upper() in ["LATENCY_TARGET", "ERROR_RATE_TARGET", "COST_TARGET"]:
            is_met = actual_value <= target_value
        else:
            is_met = actual_value >= target_value

        eval_res = RuntimeObjectiveEvaluation(
            evaluation_id=f"slo_{uuid.uuid4().hex[:12]}",
            tenant_id=tenant_id,
            target_service_id=target_service_id,
            objective_name=objective_name,
            target_value=target_value,
            actual_value=actual_value,
            is_met=is_met,
        )
        logger.info(f"Evaluated SLO '{objective_name}' for '{target_service_id}': met={is_met}")
        return eval_res
