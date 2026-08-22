"""Unit tests for IsolatedExtensionRuntime."""

import pytest
from app.extensions.extension import Extension, ExtensionManifest, ExtensionType
from app.extensions.extension_runtime import IsolatedExtensionRuntime


def test_sandboxed_extension_execution():
    runtime = IsolatedExtensionRuntime()

    m = ExtensionManifest(identifier="ext.handler", name="Handler Ext", publisher_id="p1", extension_type=ExtensionType.TOOL)
    ext = Extension(manifest=m)

    def dummy_handler(x: int, y: int) -> int:
        return x + y

    res = runtime.execute_extension_handler(ext, dummy_handler, 10, 20)
    assert res == 30
