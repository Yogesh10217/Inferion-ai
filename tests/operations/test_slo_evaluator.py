from app.operations.observability_engine import ObservabilityEngine
from app.operations.sli import SLIEvaluator
from app.operations.slo import SLOEvaluator, SLOStatus


def test_slo_evaluator_met():
    obs_engine = ObservabilityEngine()
    obs = obs_engine.collect_observations(
        app_data={"request_count": 1000, "failure_count": 0, "latency_p95": 100.0},
    )
    sli_results = SLIEvaluator().evaluate(obs)
    slo_results = SLOEvaluator().evaluate(sli_results)
    assert all(r.status == SLOStatus.MET for r in slo_results)


def test_slo_evaluator_breached():
    obs_engine = ObservabilityEngine()
    obs = obs_engine.collect_observations(
        app_data={"request_count": 1000, "failure_count": 50, "error_rate": 0.05, "latency_p95": 800.0},
    )
    sli_results = SLIEvaluator().evaluate(obs)
    slo_results = SLOEvaluator().evaluate(sli_results)
    breached = [r for r in slo_results if r.status == SLOStatus.BREACHED]
    assert len(breached) >= 1
