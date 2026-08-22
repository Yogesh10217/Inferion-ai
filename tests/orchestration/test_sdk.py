"""Integration tests for Orchestration Python SDK client."""

import pytest
from sdk.python.llm_engine.orchestration import OrchestrationClient
from sdk.python.llm_engine.client import LLMEngineClient


def test_python_sdk_orchestration_client():
    sdk = OrchestrationClient(base_url="http://localhost:8000")

    wf = sdk.create_workflow("SDK WF", steps=[{"step_id": "s1"}], tenant_id="t_sdk")
    assert wf["name"] == "SDK WF"

    case = sdk.create_case("SDK Case", tenant_id="t_sdk")
    assert case["title"] == "SDK Case"

    # Test LLMEngineClient integration
    client = LLMEngineClient(base_url="http://localhost:8000", api_key="test_key")
    assert hasattr(client, "orchestration")
