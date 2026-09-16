from enum import Enum
from typing import Dict

from .exceptions import PluginLifecycleError


class PluginState(str, Enum):
    DISCOVERED = "DISCOVERED"
    LOADED = "LOADED"
    INITIALIZED = "INITIALIZED"
    ENABLED = "ENABLED"
    RUNNING = "RUNNING"
    DISABLED = "DISABLED"
    UNLOADED = "UNLOADED"


# Allowed state transitions
VALID_TRANSITIONS = {
    PluginState.DISCOVERED: {PluginState.LOADED, PluginState.UNLOADED},
    PluginState.LOADED: {PluginState.INITIALIZED, PluginState.UNLOADED},
    PluginState.INITIALIZED: {PluginState.ENABLED, PluginState.DISABLED, PluginState.UNLOADED},
    PluginState.ENABLED: {PluginState.RUNNING, PluginState.DISABLED, PluginState.UNLOADED},
    PluginState.RUNNING: {PluginState.ENABLED, PluginState.DISABLED},
    PluginState.DISABLED: {PluginState.ENABLED, PluginState.UNLOADED},
    PluginState.UNLOADED: {PluginState.LOADED, PluginState.INITIALIZED, PluginState.DISCOVERED},
}


class PluginLifecycleManager:
    def __init__(self):
        self._states: Dict[str, PluginState] = {}

    def get_state(self, plugin_id: str) -> PluginState:
        return self._states.get(plugin_id, PluginState.UNLOADED)

    def transition_to(self, plugin_id: str, new_state: PluginState) -> PluginState:
        current_state = self.get_state(plugin_id)
        if current_state != new_state:
            allowed = VALID_TRANSITIONS.get(current_state, set())
            if new_state not in allowed:
                raise PluginLifecycleError(
                    f"Invalid state transition for plugin '{plugin_id}' from {current_state.value} to {new_state.value}"
                )
            self._states[plugin_id] = new_state
        return new_state

    async def install(self, plugin) -> None:
        await plugin.on_install()
        self._states[plugin.manifest.id] = PluginState.LOADED

    async def initialize(self, plugin) -> None:
        self.transition_to(plugin.manifest.id, PluginState.INITIALIZED)
        await plugin.on_initialize()

    async def enable(self, plugin) -> None:
        self.transition_to(plugin.manifest.id, PluginState.ENABLED)
        await plugin.on_enable()

    async def disable(self, plugin) -> None:
        self.transition_to(plugin.manifest.id, PluginState.DISABLED)
        await plugin.on_disable()

    async def uninstall(self, plugin) -> None:
        await plugin.on_uninstall()
        self.transition_to(plugin.manifest.id, PluginState.UNLOADED)
