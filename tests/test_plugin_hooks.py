import pytest
from app.plugins.plugin_hooks import PluginHook

def test_plugin_hooks():
    assert PluginHook.SYSTEM_STARTUP == "system.startup"
