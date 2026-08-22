"""Unit tests for ExtensionRegistry."""

import pytest
from app.extensions.extension import Extension, ExtensionManifest, ExtensionType
from app.extensions.extension_registry import ExtensionRegistry
from app.extensions.exceptions import ExtensionNotFoundException


def test_extension_registration_and_tenant_isolation():
    reg = ExtensionRegistry()

    m = ExtensionManifest(
        identifier="com.acme.tool",
        name="Acme Tool",
        publisher_id="pub_1",
        extension_type=ExtensionType.TOOL,
    )
    ext = Extension(manifest=m, tenant_id="tenant_a")
    reg.register_extension(ext)

    # Scoped queries
    tenant_a_exts = reg.list_extensions(tenant_id="tenant_a")
    assert len(tenant_a_exts) == 1

    tenant_b_exts = reg.list_extensions(tenant_id="tenant_b")
    assert len(tenant_b_exts) == 0
