from app.operations.prometheus_observability import PrometheusObservabilityAdapter, PrometheusRuntimeStatus


def test_prometheus_container_runtime():
    adapter = PrometheusObservabilityAdapter()
    res = adapter.evaluate_prometheus_readiness(is_container_env=True, is_production=False)
    assert res.status == PrometheusRuntimeStatus.PROMETHEUS_CONTAINER_RUNTIME_VALIDATED
    assert res.is_reachable is True


def test_prometheus_production_not_executed():
    adapter = PrometheusObservabilityAdapter()
    res = adapter.evaluate_prometheus_readiness(is_container_env=True, is_production=True)
    assert res.status == PrometheusRuntimeStatus.PROMETHEUS_PRODUCTION_RUNTIME_NOT_EXECUTED
    assert res.is_reachable is False
