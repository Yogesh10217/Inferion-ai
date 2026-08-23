"""Unit tests for Python SDK PlatformOperationsClient."""

import pytest
from unittest.mock import MagicMock
from sdk.python.llm_engine.platform_operations import PlatformOperationsClient


def test_python_sdk_platform_operations_client():
    mock_http_client = MagicMock()
    mock_http_client.get.return_value = [{"service_id": "svc_1", "name": "Gateway"}]
    mock_http_client.post.return_value = {"service_id": "svc_1", "name": "Gateway"}

    sdk_client = PlatformOperationsClient(mock_http_client)

    services = sdk_client.list_services("t1")
    assert len(services) == 1
    assert services[0]["name"] == "Gateway"

    created = sdk_client.create_service("Gateway", "t1")
    assert created["service_id"] == "svc_1"
