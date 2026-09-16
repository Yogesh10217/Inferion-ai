from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List

from app.deployment.models import ProgressiveDeliveryState, ProgressiveDeliveryStrategy


@dataclass
class ProgressiveDeliveryStepResult:
    traffic_percentage: int
    step_name: str
    status: str
    validated: bool
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ProgressiveDeliveryPlan:
    strategy: ProgressiveDeliveryStrategy
    steps: List[int]
    status: ProgressiveDeliveryState
    active_step_index: int = 0
    executed_steps: List[ProgressiveDeliveryStepResult] = field(default_factory=list)
    blocking_reasons: List[str] = field(default_factory=list)


class ProgressiveDeliveryEngine:
    """Orchestrates controlled progressive delivery strategies (Canary, Blue-Green, Rolling)."""

    CANARY_STEPS = [0, 5, 10, 25, 50, 100]

    @classmethod
    def create_delivery_plan(
        cls, strategy: ProgressiveDeliveryStrategy = ProgressiveDeliveryStrategy.CANARY
    ) -> ProgressiveDeliveryPlan:
        if strategy == ProgressiveDeliveryStrategy.CANARY:
            steps = cls.CANARY_STEPS
        elif strategy in (ProgressiveDeliveryStrategy.ALL_AT_ONCE, ProgressiveDeliveryStrategy.SIMULATION_ONLY):
            steps = [0, 100]
        elif strategy == ProgressiveDeliveryStrategy.BLUE_GREEN:
            steps = [0, 100]
        elif strategy == ProgressiveDeliveryStrategy.ROLLING:
            steps = [0, 25, 50, 75, 100]
        else:
            steps = [0, 100]

        return ProgressiveDeliveryPlan(
            strategy=strategy,
            steps=steps,
            status=ProgressiveDeliveryState.NOT_STARTED,
            active_step_index=0,
        )

    @classmethod
    def execute_next_step(
        cls,
        plan: ProgressiveDeliveryPlan,
        traffic_promoter_fn: Callable[[int], Dict[str, Any]],
        validation_fn: Callable[[int], Dict[str, Any]],
    ) -> ProgressiveDeliveryStepResult:
        if plan.active_step_index >= len(plan.steps):
            return ProgressiveDeliveryStepResult(
                traffic_percentage=plan.steps[-1] if plan.steps else 100,
                step_name="COMPLETED",
                status="COMPLETED",
                validated=True,
            )

        target_pct = plan.steps[plan.active_step_index]
        step_name = f"STEP_{plan.active_step_index + 1}_{target_pct}_PERCENT"
        plan.status = ProgressiveDeliveryState.TRAFFIC_PROMOTING

        # 1. Promote traffic
        promo_res = traffic_promoter_fn(target_pct)

        # 2. Validate traffic health at current step
        val_res = validation_fn(target_pct)
        is_healthy = val_res.get("valid", True) and val_res.get("status") not in ("FAILED", "ROLLBACK_REQUIRED")

        errors: List[str] = []
        if not is_healthy:
            errors.extend(val_res.get("errors", ["Traffic validation failure at progressive step"]))
            plan.status = ProgressiveDeliveryState.FAILED
            plan.blocking_reasons.extend(errors)
            step_result = ProgressiveDeliveryStepResult(
                traffic_percentage=target_pct,
                step_name=step_name,
                status="FAILED",
                validated=False,
                metrics=val_res.get("metrics", {}),
                errors=errors,
            )
            plan.executed_steps.append(step_result)
            return step_result

        step_result = ProgressiveDeliveryStepResult(
            traffic_percentage=target_pct,
            step_name=step_name,
            status="PASSED",
            validated=True,
            metrics=val_res.get("metrics", {}),
        )
        plan.executed_steps.append(step_result)
        plan.active_step_index += 1

        if plan.active_step_index >= len(plan.steps):
            plan.status = ProgressiveDeliveryState.COMPLETED
        else:
            plan.status = ProgressiveDeliveryState.CANARY_VALIDATING if target_pct < 100 else ProgressiveDeliveryState.FULL_VALIDATING

        return step_result
