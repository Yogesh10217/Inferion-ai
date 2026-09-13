from app.operations.error_budget import ErrorBudgetEvaluator, ErrorBudgetStatus
from app.operations.observability_engine import ObservabilityEngine
from app.operations.sli import SLIEvaluator
from app.operations.slo import SLOEvaluator


def test_error_budget_healthy():
    obs = ObservabilityEngine().collect_observations()
    sli = SLIEvaluator().evaluate(obs)
    slo = SLOEvaluator().evaluate(sli)
    eb_res = ErrorBudgetEvaluator().evaluate(slo)
    assert eb_res.status == ErrorBudgetStatus.HEALTHY
    assert eb_res.budget.remaining_budget == 100.0
    assert eb_res.budget.consumed_budget == 0.0


def test_error_budget_exhausted():
    obs = ObservabilityEngine().collect_observations(
        app_data={"request_count": 1000, "failure_count": 200, "error_rate": 0.20},
    )
    sli = SLIEvaluator().evaluate(obs)
    slo = SLOEvaluator().evaluate(sli)
    eb_res = ErrorBudgetEvaluator().evaluate(slo)
    assert eb_res.status == ErrorBudgetStatus.EXHAUSTED
    assert eb_res.budget.remaining_budget == 0.0
