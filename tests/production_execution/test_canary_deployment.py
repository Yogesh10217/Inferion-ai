from app.deployment.models import ProgressiveDeliveryState, ProgressiveDeliveryStrategy
from app.deployment.progressive_delivery import ProgressiveDeliveryEngine


def test_canary_step_by_step_execution():
    plan = ProgressiveDeliveryEngine.create_delivery_plan(strategy=ProgressiveDeliveryStrategy.CANARY)

    def promo_fn(pct):
        return {"status": "PROMOTED", "pct": pct}

    def val_fn(pct):
        return {"valid": True, "status": "PASSED"}

    for _ in range(len(plan.steps)):
        step_res = ProgressiveDeliveryEngine.execute_next_step(plan, promo_fn, val_fn)
        assert step_res.validated is True

    assert plan.status == ProgressiveDeliveryState.COMPLETED
    assert len(plan.executed_steps) == len(plan.steps)
