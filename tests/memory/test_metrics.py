"""
Tests for Memory Prometheus Metrics Registration
"""

from app.observability.prometheus_registry import PrometheusRegistry


def test_prometheus_memory_metrics_registration():
    reg = PrometheusRegistry()
    assert hasattr(reg, "memory_reads_total")
    assert hasattr(reg, "memory_writes_total")
    assert hasattr(reg, "memory_searches_total")
    assert hasattr(reg, "memory_compressions_total")
    assert hasattr(reg, "memory_summaries_total")
    assert hasattr(reg, "memory_expirations_total")
    assert hasattr(reg, "memory_embeddings_total")
    assert hasattr(reg, "memory_vector_search_total")
    assert hasattr(reg, "memory_cache_hits_total")
    assert hasattr(reg, "memory_cache_misses_total")
    assert hasattr(reg, "memory_storage_bytes")
    assert hasattr(reg, "memory_retrieval_latency_seconds")
    assert hasattr(reg, "memory_compression_latency_seconds")
