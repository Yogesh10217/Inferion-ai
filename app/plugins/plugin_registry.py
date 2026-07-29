from typing import Dict, List, Optional
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
