from app.deployment.models import ProgressiveDeliveryState, ProgressiveDeliveryStrategy
from app.deployment.progressive_delivery import ProgressiveDeliveryEngine


def test_canary_progressive_delivery_plan_creation():
    plan = ProgressiveDeliveryEngine.create_delivery_plan(strategy=ProgressiveDeliveryStrategy.CANARY)
    assert plan.strategy == ProgressiveDeliveryStrategy.CANARY
    assert plan.steps == [0, 5, 10, 25, 50, 100]
    assert plan.status == ProgressiveDeliveryState.NOT_STARTED
