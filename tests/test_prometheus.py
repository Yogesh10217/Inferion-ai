import pytest
from prometheus_client.parser import text_string_to_metric_families

from app.observability.metrics_mapper import MetricsMapper
from app.observability.prometheus_registry import PrometheusRegistry
from app.services.metrics_service import MetricsService


@pytest.mark.asyncio
async def test_metrics_endpoint_exists_and_format(get_client):
    # Make a request to trigger metrics endpoint
    async with get_client() as client:
        response = await client.get("/metrics")
        assert response.status_code == 200

        # Must have the correct prometheus text content type
        assert "text/plain" in response.headers["content-type"]
        assert "version=" in response.headers["content-type"]

        # Verify we can parse the output as valid Prometheus text format
        content = response.text
        families = list(text_string_to_metric_families(content))

        # Ensure our namespace metrics are present
        metric_names = [f.name for f in families]
        assert "llm_engine_inference_uptime_seconds" in metric_names
        assert "llm_engine_inference_api_requests" in metric_names


def test_metrics_mapper_updates_counters_and_gauges():
    metrics = MetricsService()
    registry = PrometheusRegistry(namespace="test", subsystem="sys")
    mapper = MetricsMapper(registry=registry, metrics_service=metrics, version="1.0.0")

    # Simulate activity
    metrics.record_request(150.0, is_error=False)
    metrics.record_request(200.0, is_error=True)
    metrics.record_enqueue()
    metrics.record_enqueue()
    metrics.record_dequeue(50.0)
    metrics.record_batch_dispatch(batch_size=5, delay_ms=10.0)

    mapper.synchronize()

    # Verify gauges
    assert registry.registry.get_sample_value("test_sys_scheduler_queue_depth") == 1

    # Verify counters
    assert registry.registry.get_sample_value("test_sys_api_requests_total") == 2
    assert registry.registry.get_sample_value("test_sys_api_errors_total") == 1
    assert registry.registry.get_sample_value("test_sys_scheduler_processed_total") == 1
    assert registry.registry.get_sample_value("test_sys_batching_requests_batched_total") == 5
    assert registry.registry.get_sample_value("test_sys_batching_batches_dispatched_total") == 1


def test_metrics_mapper_histogram_buffering():
    metrics = MetricsService()
    registry = PrometheusRegistry(namespace="test", subsystem="sys")
    mapper = MetricsMapper(registry=registry, metrics_service=metrics, version="1.0.0")

    metrics.record_request(150.0, is_error=False)  # 0.15s
    metrics.record_request(1200.0, is_error=False)  # 1.2s

    mapper.synchronize()

    # After sync, the buffers in metrics should be cleared
    assert len(metrics._recent_request_latencies) == 0

    # Check that the histogram received the observations
    count = registry.registry.get_sample_value("test_sys_api_request_duration_seconds_count")
    sum_val = registry.registry.get_sample_value("test_sys_api_request_duration_seconds_sum")

    assert count == 2
    assert sum_val == pytest.approx(1.35)  # 0.15 + 1.20

    # Test Provider metrics
    metrics.record_provider_latency("openai", "openai-1", 300.0)
    mapper.synchronize()

    prov_count = registry.registry.get_sample_value(
        "test_sys_provider_latency_seconds_count", {"provider_id": "openai", "instance_id": "openai-1"}
    )
    assert prov_count == 1
    assert (
        registry.registry.get_sample_value(
            "test_sys_provider_latency_seconds_sum", {"provider_id": "openai", "instance_id": "openai-1"}
        )
        == 0.3
    )
