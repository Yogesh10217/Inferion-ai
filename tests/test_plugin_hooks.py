import pytest
from app.plugins.plugin_manager import PluginManager
from app.plugins.plugin_hooks import PluginHook


@pytest.mark.asyncio
async def test_plugin_hook_execution():
    manager = PluginManager()
    await manager.load_plugins()
    await manager.enable_plugin("response_modifier")

    res = await manager.dispatch_hook(PluginHook.AFTER_REQUEST, {"status": "ok"})
    assert len(res) >= 1
    assert res[0].get("processed_by_plugin") is True
