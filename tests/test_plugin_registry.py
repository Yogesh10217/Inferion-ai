import pytest
from app.plugins.plugin_registry import PluginRegistry

def test_plugin_registry():
    registry = PluginRegistry()
    assert registry is not None
