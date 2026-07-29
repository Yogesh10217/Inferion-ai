import logging
from typing import Dict, List
from .plugin import Plugin
from .plugin_registry import PluginRegistry
from .plugin_lifecycle import PluginLifecycleManager
from .plugin_loader import PluginLoader
from .plugin_execution import PluginExecutor

logger = logging.getLogger(__name__)

class PluginManager:
    def __init__(self):
        self.registry = PluginRegistry()
        self.lifecycle = PluginLifecycleManager()
        self.loader = PluginLoader()
        self.executor = PluginExecutor()
        
    async def initialize(self):
        logger.info("Initializing PluginManager")
        
    async def load_plugins(self):
        logger.info("Loading plugins...")

    async def dispatch_hook(self, hook_name: str, *args, **kwargs):
        enabled_plugins = self.registry.get_enabled()
        for plugin in enabled_plugins:
            # Check if plugin subscribes to hook (simplified)
            handler = getattr(plugin, f"on_{hook_name.replace('.', '_')}", None)
            if handler:
                await self.executor.execute(plugin.manifest.id, handler, *args, **kwargs)
