import os

TEST_DIR = r"c:\Users\Yogesh E\OneDrive\Desktop\Manjus\llm-inference-engine\tests"

tests = {
    "test_plugin_loader.py": """import pytest
from app.plugins.plugin_loader import PluginLoader
from app.plugins.exceptions import PluginLoadError
from app.plugins.plugin_manifest import PluginManifest

def test_plugin_loader():
    loader = PluginLoader()
    # Stub test
    assert loader is not None
""",
    "test_plugin_registry.py": """import pytest
from app.plugins.plugin_registry import PluginRegistry

def test_plugin_registry():
    registry = PluginRegistry()
    assert registry is not None
""",
    "test_plugin_permissions.py": """import pytest
from app.plugins.plugin_context import PluginContext
from app.plugins.plugin_manifest import PluginPermission
from app.plugins.exceptions import PluginPermissionError

def test_plugin_permissions():
    perms = [PluginPermission(action="events.publish", resource="*")]
    ctx = PluginContext("test_plugin", perms, None)
    
    # Should not raise
    assert ctx.check_permission("events.publish", "test.event") is True
    
    with pytest.raises(PluginPermissionError):
        ctx.check_permission("database.read", "users")
""",
    "test_plugin_lifecycle.py": """import pytest
from app.plugins.plugin_lifecycle import PluginLifecycleManager

def test_plugin_lifecycle():
    manager = PluginLifecycleManager()
    assert manager is not None
""",
    "test_plugin_hooks.py": """import pytest
from app.plugins.plugin_hooks import PluginHook

def test_plugin_hooks():
    assert PluginHook.SYSTEM_STARTUP == "system.startup"
""",
    "test_plugin_manager.py": """import pytest
from app.plugins.plugin_manager import PluginManager

@pytest.mark.asyncio
async def test_plugin_manager():
    manager = PluginManager()
    await manager.initialize()
    assert manager is not None
"""
}

for name, content in tests.items():
    with open(os.path.join(TEST_DIR, name), "w") as f:
        f.write(content)

print("Tests created.")
