from __future__ import annotations

import pytest
from app.deployment.container_validation import ContainerValidationEngine


def test_invalid_image_digest_format():
    valid, msg = ContainerValidationEngine.validate_image_digest("invalid-digest-no-sha256")
    assert valid is False
    assert "must use sha256: prefix" in msg


def test_invalid_hex_length_digest():
    valid, msg = ContainerValidationEngine.validate_image_digest("sha256:abc123short")
    assert valid is False
    assert "must contain exactly 64 hexadecimal characters" in msg


def test_artifact_mismatch_detection():
    exp = "sha256:29069a7755b4e7fb2cb2087977de57c745c28ecf636026be9c6b32e23d251762"
    act = "sha256:1111111111111111111111111111111111111111111111111111111111111111"

    valid, msg = ContainerValidationEngine.validate_runtime_artifact(exp, act)
    assert valid is False
    assert "DEPLOYMENT_ARTIFACT_MISMATCH" in msg
