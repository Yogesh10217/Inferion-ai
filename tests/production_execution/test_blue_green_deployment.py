from app.deployment.models import ProgressiveDeliveryState, ProgressiveDeliveryStrategy
from app.deployment.progressive_delivery import ProgressiveDeliveryEngine


def test_blue_green_delivery_plan():
    plan = ProgressiveDeliveryEngine.create_delivery_plan(strategy=ProgressiveDeliveryStrategy.BLUE_GREEN)
    assert plan.strategy == ProgressiveDeliveryStrategy.BLUE_GREEN
    assert plan.steps == [0, 100]

    def promo_fn(pct):
        return {"status": "PROMOTED", "pct": pct}

    def val_fn(pct):
        return {"valid": True, "status": "PASSED"}

    ProgressiveDeliveryEngine.execute_next_step(plan, promo_fn, val_fn)
    ProgressiveDeliveryEngine.execute_next_step(plan, promo_fn, val_fn)
    assert plan.status == ProgressiveDeliveryState.COMPLETED
