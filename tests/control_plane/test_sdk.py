"""Unit tests for Python SDK ControlPlaneClient."""

import pytest
from sdk.python.llm_engine.control_plane import ControlPlaneClient


def test_sdk_client_instantiation():
    sdk = ControlPlaneClient("http://localhost:8002")
    assert sdk.base_url == "http://localhost:8002"
