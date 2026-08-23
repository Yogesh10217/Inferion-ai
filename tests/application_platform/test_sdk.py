"""Unit tests for Multi-Language SDK integration."""

import pytest
from sdk.python.llm_engine import LLMEngineClient, ApplicationPlatformClient


def test_python_sdk_application_client():
    client = LLMEngineClient()
    assert hasattr(client, "applications")

    res = client.applications.create_application("SDK Copilot", "COPILOT", tenant_id="tenant_sdk")
    assert res["name"] == "SDK Copilot"
    assert res["status"] == "DRAFT"

    ver = client.applications.create_version(res["application_id"], "1.0.0", "tenant_sdk")
    assert ver["version"] == "1.0.0"
