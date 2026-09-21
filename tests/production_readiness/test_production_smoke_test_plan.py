from __future__ import annotations

from app.deployment.production_smoke_test import ProductionSmokeTestPlanEvaluator


def test_smoke_test_plan_target_safety():
    plan = ProductionSmokeTestPlanEvaluator.evaluate_smoke_test_plan(target_url="http://127.0.0.1:8003")

    assert plan.target_url == "http://127.0.0.1:8003"
    assert plan.execution_status == "SMOKE_TEST_PLAN_READY"
    assert len(plan.test_cases) == 8


def test_smoke_test_plan_rejects_auto_production():
    plan = ProductionSmokeTestPlanEvaluator.evaluate_smoke_test_plan(target_url="http://api.production-domain.com")

    assert plan.execution_status == "PRODUCTION_SMOKE_TEST_NOT_EXECUTED"
