import pytest

from app.plugins.plugin_manager import PluginManager


@pytest.mark.asyncio
async def test_plugin_manager_lifecycle():
    manager = PluginManager()
    discovered = await manager.load_plugins()
    assert len(discovered) > 0
    assert "hello_world" in discovered

    # Enable hello_world
    await manager.enable_plugin("hello_world")
    plugin = manager.registry.get("hello_world")
    assert plugin is not None
    assert plugin.is_enabled is True

    # Dispatch hook
    results = await manager.dispatch_hook("before_request", {"model": "gpt-4"})
    assert len(results) >= 1

    # Disable plugin
    await manager.disable_plugin("hello_world")
    assert plugin.is_enabled is False


@pytest.mark.asyncio
async def test_plugin_manager_reload_and_health():
    manager = PluginManager()
    await manager.load_plugins()
    health = manager.get_plugin_health("hello_world")
    assert health["plugin_id"] == "hello_world"
    assert health["health"] == "healthy"

    reloaded = await manager.reload_plugin("hello_world")
    assert reloaded.manifest.id == "hello_world"
