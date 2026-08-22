"""Integration tests for Identity Python SDK client."""

import pytest
from sdk.python.llm_engine.identity import IdentityClient
from sdk.python.llm_engine.client import LLMEngineClient


def test_python_sdk_identity_client():
    sdk = IdentityClient(base_url="http://localhost:8000")

    ident = sdk.create_identity("sdk_user", identity_type="HUMAN", tenant_id="t_sdk")
    assert ident["username"] == "sdk_user"
    assert ident["status"] == "ACTIVE"

    auth = sdk.authenticate("id_123", method="JWT")
    assert auth["is_authenticated"] is True

    # Test LLMEngineClient integration
    client = LLMEngineClient(base_url="http://localhost:8000", api_key="test_key")
    assert hasattr(client, "identity_platform")
