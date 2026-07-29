import pytest
from app.plugins.plugin_manager import PluginManager

@pytest.mark.asyncio
async def test_plugin_manager():
    manager = PluginManager()
    await manager.initialize()
    assert manager is not None
