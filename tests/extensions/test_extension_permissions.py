"""Unit tests for ExtensionPermissionEngine capability escalation blocking."""

import pytest

from app.extensions.exceptions import ExtensionSecurityViolationException
from app.extensions.extension import Extension, ExtensionManifest, ExtensionType
from app.extensions.extension_permissions import ExtensionPermissionEngine


def test_permission_escalation_blocking():
    pe = ExtensionPermissionEngine()

    m = ExtensionManifest(
        identifier="com.test.secure",
        name="Secure Ext",
        publisher_id="pub_1",
        extension_type=ExtensionType.TOOL,
        required_permissions=["read"],
    )
    ext = Extension(manifest=m, tenant_id="t1")

    # Allowed action
    assert pe.validate_extension_permissions(ext, "read", tenant_id="t1") is True

    # Cross-tenant attempt fails
    with pytest.raises(ExtensionSecurityViolationException):
        pe.validate_extension_permissions(ext, "read", tenant_id="t2")

    # Unpermitted permission escalation attempt fails
    with pytest.raises(ExtensionSecurityViolationException):
        pe.validate_extension_permissions(ext, "secret:read", tenant_id="t1")
