"""Unit tests for Python SDK IntegrationClient."""

from sdk.python.llm_engine.client import LLMEngineClient
from sdk.python.llm_engine.integrations import IntegrationClient


def test_python_sdk_integration_client():
    client = LLMEngineClient(base_url="http://localhost:8000")
    assert hasattr(client, "integrations")
    assert isinstance(client.integrations, IntegrationClient)

    res = client.integrations.register_integration("Slack SDK Test", category="COMMUNICATION", tenant_id="t_sdk")
    assert res["name"] == "Slack SDK Test"
