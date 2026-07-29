import pytest
from app.plugins.plugin_loader import PluginLoader
from app.plugins.exceptions import PluginLoadError
from app.plugins.plugin_manifest import PluginManifest

def test_plugin_loader():
    loader = PluginLoader()
    # Stub test
    assert loader is not None
