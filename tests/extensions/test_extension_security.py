"""Unit tests for ExtensionSecurityEngine SHA-256 verification and approval gating."""

import pytest

from app.extensions.exceptions import ExtensionSecurityViolationException
from app.extensions.extension import ExtensionManifest, ExtensionType
from app.extensions.security import ExtensionSecurityEngine


def test_sha256_checksum_and_approval_requirement():
    engine = ExtensionSecurityEngine()

    pkg_data = b"extension package binary content"
    expected_hash = "b8178e12049345bc2ae6fbf8ab8b4d885f507d5505d61868a8ff571fb3ca37be"

    # Valid SHA-256
    assert engine.verify_package_checksum(pkg_data, expected_hash) is True

    # Invalid SHA-256 fails
    with pytest.raises(ExtensionSecurityViolationException):
        engine.verify_package_checksum(pkg_data, "bad_hash")

    # High-risk permissions require approval
    m_high = ExtensionManifest(
        identifier="ext.risk",
        name="Risk Ext",
        publisher_id="p1",
        extension_type=ExtensionType.TOOL,
        required_permissions=["shell:execute"],
    )
    report = engine.analyze_extension_security(m_high)
    assert report.requires_approval is True
    assert "shell:execute" in report.detected_high_risk_permissions
