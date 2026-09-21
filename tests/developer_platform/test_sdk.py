"""Unit tests for Python SDK DeveloperPlatformClient."""

from sdk.python.llm_engine.client import LLMEngineClient
from sdk.python.llm_engine.developer_platform import DeveloperPlatformClient


def test_python_sdk_developer_platform_client():
    client = LLMEngineClient(base_url="http://localhost:8000")
    assert hasattr(client, "developer_platform")
    assert isinstance(client.developer_platform, DeveloperPlatformClient)

    res = client.developer_platform.create_project("SDK Project", tenant_id="t_sdk_dev")
    assert res["name"] == "SDK Project"
