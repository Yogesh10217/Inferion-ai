"""Unit tests for ExtensionLifecycleManager atomic upgrade and rollback."""

import pytest
from app.extensions.extension import Extension, ExtensionManifest, ExtensionVersion, ExtensionType
from app.extensions.extension_lifecycle import ExtensionLifecycleManager, ExtensionLifecycleState


def test_extension_atomic_upgrade_and_rollback():
    lm = ExtensionLifecycleManager()

    m1 = ExtensionManifest(identifier="ext.test", name="Ext Test", version="1.0.0", publisher_id="p1", extension_type=ExtensionType.TOOL)
    ext = Extension(manifest=m1, current_version="1.0.0")

    v1 = ExtensionVersion(version_number="1.0.0", manifest=m1, package_checksum_sha256="abc")
    ext.versions.append(v1)

    lm.enable_extension(ext)
    assert ext.is_enabled is True

    # Upgrade to 2.0.0
    m2 = ExtensionManifest(identifier="ext.test", name="Ext Test", version="2.0.0", publisher_id="p1", extension_type=ExtensionType.TOOL)
    v2 = ExtensionVersion(version_number="2.0.0", manifest=m2, package_checksum_sha256="xyz")

    lm.upgrade_extension(ext, v2)
    assert ext.current_version == "2.0.0"

    # Rollback to 1.0.0
    lm.rollback_extension(ext, "1.0.0")
    assert ext.current_version == "1.0.0"
