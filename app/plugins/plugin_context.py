import logging
from typing import Any, Dict

class PluginContext:
    def __init__(self, plugin_id: str, permissions: list, event_bus: Any):
        self.plugin_id = plugin_id
        self._permissions = permissions
        self._event_bus = event_bus
        self.logger = logging.getLogger(f"plugin.{plugin_id}")
        self.settings: Dict[str, Any] = {}
        
    def check_permission(self, action: str, resource: str):
        for p in self._permissions:
            if p.action == action and (p.resource == resource or p.resource == "*"):
                return True
        from .exceptions import PluginPermissionError
        raise PluginPermissionError(f"Plugin {self.plugin_id} lacks permission {action} on {resource}")

    async def publish_event(self, event_type: str, data: dict):
        self.check_permission("events.publish", event_type)
        await self._event_bus.publish(event_type, data)
