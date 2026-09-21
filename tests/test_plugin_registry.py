from app.plugins.plugin import Plugin
from app.plugins.plugin_context import PluginContext
from app.plugins.plugin_manifest import PluginManifest
from app.plugins.plugin_registry import PluginRegistry


def test_plugin_registry_persistence(tmp_path):
    persist_file = str(tmp_path / "registry.json")
    registry = PluginRegistry(persistence_file=persist_file)

    manifest = PluginManifest(
        id="test_reg_plugin",
        name="Test",
        version="1.0.0",
        description="Test",
        author="Author",
        license="MIT",
        entrypoint="plugin.py:Plugin",
    )
    context = PluginContext("test_reg_plugin", [], None)
    plugin = Plugin(manifest, context)

    registry.register(plugin, enabled=True)
    assert len(registry.get_enabled()) == 1

    # Instantiate new registry reading from persistence file
    registry2 = PluginRegistry(persistence_file=persist_file)
    rec = registry2.get_record("test_reg_plugin")
    assert rec is not None
    assert rec.enabled is True
