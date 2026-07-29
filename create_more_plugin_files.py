import os

PLUGIN_DIR = r"c:\Users\Yogesh E\OneDrive\Desktop\Manjus\llm-inference-engine\app\plugins"
os.makedirs(PLUGIN_DIR, exist_ok=True)

files = {
    "plugin_execution.py": """import asyncio
import logging
from typing import Callable, Any
from .exceptions import PluginExecutionError

logger = logging.getLogger(__name__)

class PluginExecutor:
    def __init__(self, default_timeout: float = 5.0):
        self.default_timeout = default_timeout

    async def execute(self, plugin_id: str, func: Callable, *args, timeout: float = None, **kwargs) -> Any:
        timeout_val = timeout if timeout is not None else self.default_timeout
        try:
            # Enforce execution boundary and timeout
            return await asyncio.wait_for(func(*args, **kwargs), timeout=timeout_val)
        except asyncio.TimeoutError:
            logger.error(f"Plugin {plugin_id} timed out after {timeout_val}s")
            raise PluginExecutionError(f"Plugin {plugin_id} execution timed out")
        except Exception as e:
            logger.exception(f"Plugin {plugin_id} encountered an error: {str(e)}")
            raise PluginExecutionError(f"Plugin {plugin_id} execution failed: {str(e)}")
""",
    "plugin_registry.py": """from typing import Dict, List, Optional
from .plugin import Plugin

class PluginRegistry:
    def __init__(self):
        self._plugins: Dict[str, Plugin] = {}

    def register(self, plugin: Plugin):
        self._plugins[plugin.manifest.id] = plugin

    def unregister(self, plugin_id: str):
        if plugin_id in self._plugins:
            del self._plugins[plugin_id]

    def get(self, plugin_id: str) -> Optional[Plugin]:
        return self._plugins.get(plugin_id)

    def get_all(self) -> List[Plugin]:
        return list(self._plugins.values())

    def get_enabled(self) -> List[Plugin]:
        return [p for p in self._plugins.values() if p.is_enabled]
""",
    "plugin_api.py": """from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict

router = APIRouter(prefix="/v1/plugins", tags=["plugins"])

# In a real scenario, PluginManager would be injected via dependency injection
@router.get("/")
async def list_plugins():
    # Return list of installed plugins
    return {"plugins": []}

@router.get("/{plugin_id}")
async def get_plugin(plugin_id: str):
    return {"plugin_id": plugin_id, "status": "unknown"}

@router.post("/install")
async def install_plugin(manifest_url: str):
    return {"status": "installed"}

@router.patch("/{plugin_id}/enable")
async def enable_plugin(plugin_id: str):
    return {"status": "enabled"}

@router.patch("/{plugin_id}/disable")
async def disable_plugin(plugin_id: str):
    return {"status": "disabled"}

@router.delete("/{plugin_id}")
async def uninstall_plugin(plugin_id: str):
    return {"status": "uninstalled"}

@router.post("/{plugin_id}/reload")
async def reload_plugin(plugin_id: str):
    return {"status": "reloaded"}

@router.post("/{plugin_id}/restart")
async def restart_plugin(plugin_id: str):
    return {"status": "restarted"}

@router.get("/{plugin_id}/health")
async def plugin_health(plugin_id: str):
    return {"status": "healthy"}
""",
    "plugin_lifecycle.py": """from .plugin import Plugin
from .exceptions import PluginLifecycleError

class PluginLifecycleManager:
    async def install(self, plugin: Plugin):
        await plugin.on_install()

    async def initialize(self, plugin: Plugin):
        await plugin.on_initialize()

    async def enable(self, plugin: Plugin):
        await plugin.on_enable()

    async def disable(self, plugin: Plugin):
        await plugin.on_disable()

    async def uninstall(self, plugin: Plugin):
        await plugin.on_uninstall()
"""
}

for name, content in files.items():
    path = os.path.join(PLUGIN_DIR, name)
    with open(path, "w") as f:
        f.write(content)

print("More plugin files created.")
