from sdk.python.llm_engine import ChatCompletionRequest, LLMEngineClient


def test_python_sdk_import_and_models():
    client = LLMEngineClient(base_url="http://localhost:8000", api_key="test_key")
    req = ChatCompletionRequest(model="gpt-4", messages=[{"role": "user", "content": "SDK Test"}])
    assert client.base_url == "http://localhost:8000"
    assert req.model == "gpt-4"
