"""SDK unit tests for Python ObservabilityClient."""

import pytest
import httpx
from sdk.python.llm_engine.observability import ObservabilityClient


def test_sdk_observability_client_initialization():
    transport = httpx.MockTransport(lambda req: httpx.Response(200, json={"status": "HEALTHY"}))
    with httpx.Client(transport=transport) as http_client:
        client = ObservabilityClient(http_client, "http://test-server")
        status = client.get_status()
        assert status["status"] == "HEALTHY"
