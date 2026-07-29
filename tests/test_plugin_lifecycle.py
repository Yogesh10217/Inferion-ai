import pytest
from app.plugins.plugin_lifecycle import PluginLifecycleManager

def test_plugin_lifecycle():
    manager = PluginLifecycleManager()
    assert manager is not None
