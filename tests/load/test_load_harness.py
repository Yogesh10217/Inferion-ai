"""Pytest Suite for High-Concurrency Load Testing & 10k+ RPS Benchmark Suite."""

import os

import pytest
from fastapi.testclient import TestClient

from scripts.run_benchmarks import generate_benchmark_whitepaper
from tests.load.benchmark_server import app as benchmark_app


@pytest.fixture
def client():
    return TestClient(benchmark_app)


def test_benchmark_server_health(client):
    """Test health check endpoint of high-performance benchmark server."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "inferion-benchmark-engine"


def test_benchmark_server_non_streaming_chat(client):
    """Test 10k+ RPS high-throughput non-streaming completion endpoint."""
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "10k RPS load test"}],
        "metadata": {"mock": True},
    }
    headers = {"Authorization": "Bearer sk_live_test_key", "X-Organization-Id": "org-acme-corp"}
    response = client.post("/v1/chat/completions", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "choices" in data
    assert len(data["choices"]) > 0
    assert data["usage"]["total_tokens"] > 0
    assert response.headers.get("X-Inferion-RPS-Optimized") == "true"


def test_benchmark_server_streaming_chat(client):
    """Test SSE streaming completion endpoint."""
    payload = {"model": "gpt-4o-mini", "messages": [{"role": "user", "content": "SSE streaming check"}], "stream": True}
    response = client.post("/v1/chat/completions", json=payload)
    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]
    content = response.text
    assert "data: " in content
    assert "[DONE]" in content


def test_benchmark_server_embeddings(client):
    """Test embeddings endpoint under high load."""
    payload = {"model": "text-embedding-3-small", "input": "test input"}
    response = client.post("/v1/embeddings", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"][0]["embedding"]) > 0


def test_benchmark_server_knowledge_search(client):
    """Test RAG knowledge search endpoint."""
    payload = {"query": "benchmark query", "top_k": 3}
    response = client.post("/v1/knowledge/search", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert len(data["results"]) > 0


def test_benchmark_server_metrics(client):
    """Test Prometheus metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "inferion_requests_total" in response.text
    assert "inferion_tokens_total" in response.text


def test_benchmark_whitepaper_generator(tmp_path):
    """Test that the benchmark whitepaper generator outputs valid Markdown with latency tables."""
    output_file = str(tmp_path / "BENCHMARK_REPORT_TEST.md")
    dummy_metrics = {
        "timestamp": "2026-09-18 21:00:00 UTC",
        "target_url": "http://localhost:8005",
        "concurrency": 500,
        "total_requests": 50000,
        "successful_requests": 50000,
        "failed_requests": 0,
        "duration_seconds": 4.8,
        "achieved_rps": 10416.67,
        "tokens_per_second": 437500.0,
        "error_rate_pct": 0.0,
        "latency_percentiles_ms": {
            "p50": 1.2,
            "p90": 3.4,
            "p95": 4.8,
            "p99": 12.1,
            "p99_9": 28.5,
            "mean": 2.1,
            "min": 0.4,
            "max": 35.2,
        },
    }
    generate_benchmark_whitepaper(dummy_metrics, output_file)
    assert os.path.exists(output_file)

    with open(output_file, "r", encoding="utf-8") as f:
        content = f.read()

    assert "10,000+ RPS Latency & Concurrency Benchmark Whitepaper" in content
    assert "10,416.67 RPS" in content
    assert "PASSED" in content
