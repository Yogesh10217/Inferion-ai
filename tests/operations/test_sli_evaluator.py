from app.operations.observability_engine import ObservabilityEngine
from app.operations.sli import SLIEvaluator, SLIType


def test_sli_evaluator_all_satisfactory():
    obs_engine = ObservabilityEngine()
    obs = obs_engine.collect_observations(
        app_data={"request_count": 1000, "failure_count": 0, "latency_p95": 100.0},
        health_data={"live": True, "ready": True, "health": True},
    )
    evaluator = SLIEvaluator()
    results = evaluator.evaluate(obs)
    assert len(results) == 9
    assert all(r.is_satisfactory for r in results)


def test_sli_evaluator_unsatisfactory_error_rate():
    obs_engine = ObservabilityEngine()
    obs = obs_engine.collect_observations(
        app_data={"request_count": 1000, "failure_count": 50, "error_rate": 0.05, "latency_p95": 600.0},
    )
    evaluator = SLIEvaluator()
    results = evaluator.evaluate(obs)
    err_res = next(r for r in results if r.sli_type == SLIType.ERROR_RATE)
    assert not err_res.is_satisfactory
