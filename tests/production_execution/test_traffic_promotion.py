from app.deployment.models import ProgressiveDeliveryState, ProgressiveDeliveryStrategy
from app.deployment.progressive_delivery import ProgressiveDeliveryEngine


def test_traffic_promotion_halted_on_error():
    plan = ProgressiveDeliveryEngine.create_delivery_plan(strategy=ProgressiveDeliveryStrategy.CANARY)

    def promo_fn(pct):
        return {"status": "PROMOTED", "pct": pct}

    def val_fn(pct):
        if pct >= 10:
            return {"valid": False, "status": "FAILED", "errors": ["Traffic error rate spike"]}
        return {"valid": True, "status": "PASSED"}

    # Step 1 (0%) -> PASSED
    res0 = ProgressiveDeliveryEngine.execute_next_step(plan, promo_fn, val_fn)
    assert res0.validated is True

    # Step 2 (5%) -> PASSED
    res5 = ProgressiveDeliveryEngine.execute_next_step(plan, promo_fn, val_fn)
    assert res5.validated is True

    # Step 3 (10%) -> FAILED
    res10 = ProgressiveDeliveryEngine.execute_next_step(plan, promo_fn, val_fn)
    assert res10.validated is False
    assert plan.status == ProgressiveDeliveryState.FAILED
