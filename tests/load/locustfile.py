"""Locust Load Test Suite for Inferion AI Engine."""

from locust import HttpUser, task, between
import json


class InferenceEngineUser(HttpUser):
    """Simulates concurrent client requests against the Inferion AI LLM inference engine."""

    wait_time = between(0.1, 0.5)

    @task(3)
    def test_non_streaming_chat_completion(self):
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": "You are a helpful customer support agent."},
                {"role": "user", "content": "What is the status of my order #12345?"}
            ],
            "metadata": {"mock": True}
        }
        headers = {
            "Authorization": "Bearer sk_test_mockkey",
            "X-Organization-Id": "test_org_id",
            "Content-Type": "application/json"
        }
        with self.client.post("/v1/chat/completions", json=payload, headers=headers, catch_response=True) as response:
            if response.status_code == 200:
                data = response.json()
                if "choices" in data and len(data["choices"]) > 0:
                    response.success()
                else:
                    response.failure("Response missing choices payload")
            else:
                response.failure(f"HTTP Status {response.status_code}: {response.text}")

    @task(1)
    def test_streaming_chat_completion(self):
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "user", "content": "Explain quantum computing in 2 sentences."}
            ],
            "stream": True,
            "metadata": {"mock": True}
        }
        headers = {
            "Authorization": "Bearer sk_test_mockkey",
            "X-Organization-Id": "test_org_id",
            "Content-Type": "application/json"
        }
        with self.client.post("/v1/chat/completions", json=payload, headers=headers, stream=True, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Streaming HTTP Status {response.status_code}: {response.text}")
