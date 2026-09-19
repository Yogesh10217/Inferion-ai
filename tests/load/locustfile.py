"""Locust High-Concurrency Load Test Suite for Inferion AI Engine (10,000+ RPS Target)."""

import json
import random
import time
from locust import FastHttpUser, task, between, LoadTestShape, events


TENANTS = ["org-acme-corp", "org-techstart", "org-apex-global", "org-fin-analytics"]
WORKSPACES = ["ws-engineering", "ws-finance", "ws-data-science", "ws-ai-research"]
MODELS = ["gpt-4o-mini", "llama3", "claude-3-5-sonnet", "gpt-4o"]


class HighConcurrencyInferenceUser(FastHttpUser):
    """Simulates ultra-high throughput client workloads targeting 10,000+ RPS sustained load."""

    # Zero delay between tasks for maximum load generation
    wait_time = between(0.001, 0.005)

    def on_start(self):
        self.tenant = random.choice(TENANTS)
        self.workspace = random.choice(WORKSPACES)
        self.headers = {
            "Authorization": f"Bearer sk_live_{self.workspace}_{random.randint(1000, 9999)}",
            "X-Organization-Id": self.tenant,
            "X-Workspace-Id": self.workspace,
            "Content-Type": "application/json",
        }

    @task(40)
    def test_non_streaming_chat_completion(self):
        payload = {
            "model": random.choice(MODELS),
            "messages": [
                {"role": "system", "content": "You are a high-performance routing test payload."},
                {"role": "user", "content": "Evaluate latency for high-concurrency 10k RPS benchmark."}
            ],
            "metadata": {"mock": True, "benchmark": "10k_rps"}
        }
        with self.client.post("/v1/chat/completions", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Chat Completion failed with HTTP {response.status_code}: {response.text}")

    @task(30)
    def test_streaming_chat_completion(self):
        payload = {
            "model": random.choice(MODELS),
            "messages": [
                {"role": "user", "content": "Stream response chunk validation for 10k RPS load test."}
            ],
            "stream": True,
            "metadata": {"mock": True, "benchmark": "10k_rps"}
        }
        with self.client.post("/v1/chat/completions", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Streaming Completion failed with HTTP {response.status_code}: {response.text}")

    @task(15)
    def test_embeddings_generation(self):
        payload = {
            "model": "text-embedding-3-small",
            "input": "Inferion AI multi-tenant embedding high-throughput benchmark text."
        }
        with self.client.post("/v1/embeddings", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Embeddings failed with HTTP {response.status_code}: {response.text}")

    @task(10)
    def test_knowledge_rag_search(self):
        payload = {
            "query": "high concurrency 10k RPS benchmark performance",
            "top_k": 5,
            "vector_store": "FAISS"
        }
        with self.client.post("/v1/knowledge/search", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"RAG Search failed with HTTP {response.status_code}: {response.text}")

    @task(5)
    def test_agent_execution(self):
        payload = {
            "agent_id": "agt-dev-assistant",
            "prompt": "Run automated test verification",
            "strategy": "ReAct"
        }
        with self.client.post("/v1/agents/execute", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Agent Execution failed with HTTP {response.status_code}: {response.text}")


class Ramp10kLoadShape(LoadTestShape):
    """Custom load shape ramping up to 10,000+ RPS step profile."""

    stages = [
        {"duration": 10, "users": 100, "spawn_rate": 50},    # Warm-up ~ 1,000 RPS
        {"duration": 30, "users": 500, "spawn_rate": 100},   # Medium ~ 5,000 RPS
        {"duration": 60, "users": 1200, "spawn_rate": 200},  # Peak ~ 10,000+ RPS
        {"duration": 90, "users": 1200, "spawn_rate": 200},  # Sustained Peak 10k RPS
        {"duration": 100, "users": 0, "spawn_rate": 300},    # Cool-down
    ]

    def tick(self):
        run_time = self.get_run_time()
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
        return None
