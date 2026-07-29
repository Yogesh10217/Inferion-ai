import pytest
from llm_engine import LLMEngineClient, ChatCompletionRequest, APIKeyAuth

def test_client_init():
    client = LLMEngineClient(base_url="http://localhost:8000", api_key="my_secret_key")
    assert client.base_url == "http://localhost:8000"
    assert client.client.headers["X-API-Key"] == "my_secret_key"

def test_request_model():
    req = ChatCompletionRequest(model="gpt-4", messages=[{"role": "user", "content": "test"}])
    assert req.model == "gpt-4"
    assert req.messages[0].role == "user"
