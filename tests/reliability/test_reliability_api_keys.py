"""Unit tests for APIKeyManager."""

import pytest

from app.security.api_keys import APIKeyManager
from app.security.exceptions import InvalidAPIKeyError


def test_generate_and_verify_api_key():
    mgr = APIKeyManager()
    res = mgr.generate_api_key(name="test-key", tenant_id="tenant_x")

    raw_key = res["raw_key"]
    key_id = res["key_id"]

    # Raw key string is prefixed
    assert raw_key.startswith("sk-live-")

    # Verify key
    verified = mgr.verify_api_key(raw_key)
    assert verified.id == key_id
    assert verified.tenant_id == "tenant_x"
    assert verified.usage_count == 1


def test_revoke_and_rotate_api_key():
    mgr = APIKeyManager()
    res = mgr.generate_api_key(name="old-key")
    raw_key = res["raw_key"]
    key_id = res["key_id"]

    # Rotate key
    rotated_res = mgr.rotate_api_key(key_id)
    new_raw = rotated_res["raw_key"]

    # Old key is revoked and fails verification
    with pytest.raises(InvalidAPIKeyError):
        mgr.verify_api_key(raw_key)

    # New key succeeds
    new_verified = mgr.verify_api_key(new_raw)
    assert new_verified.id == rotated_res["key_id"]
