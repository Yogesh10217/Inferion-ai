from .plugin import Plugin
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
