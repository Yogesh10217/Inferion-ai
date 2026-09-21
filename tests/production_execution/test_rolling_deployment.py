from app.deployment.models import ProgressiveDeliveryStrategy
from app.deployment.progressive_delivery import ProgressiveDeliveryEngine


def test_rolling_delivery_plan():
    plan = ProgressiveDeliveryEngine.create_delivery_plan(strategy=ProgressiveDeliveryStrategy.ROLLING)
    assert plan.strategy == ProgressiveDeliveryStrategy.ROLLING
    assert plan.steps == [0, 25, 50, 75, 100]
