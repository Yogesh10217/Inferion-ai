"""Integration tests for Knowledge Platform Python SDK client."""

import pytest
from sdk.python.llm_engine.knowledge_platform import KnowledgePlatformClient
from sdk.python.llm_engine.client import LLMEngineClient


def test_python_sdk_knowledge_platform_client():
    sdk = KnowledgePlatformClient(base_url="http://localhost:8000")

    item = sdk.create_knowledge("SDK Doc", "Content", tenant_id="t_sdk_kp")
    assert item["title"] == "SDK Doc"

    res = sdk.retrieve("query", tenant_id="t_sdk_kp")
    assert res["query"] == "query"

    # Test LLMEngineClient integration
    client = LLMEngineClient(base_url="http://localhost:8000", api_key="test_key")
    assert hasattr(client, "knowledge_platform")
