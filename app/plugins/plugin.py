from .plugin_context import PluginContext
from .plugin_manifest import PluginManifest


class Plugin:
    def __init__(self, manifest: PluginManifest, context: PluginContext):
        self.manifest = manifest
        self.context = context
        self.is_enabled = False

    async def on_install(self):
        pass

    async def on_initialize(self):
        pass

    async def on_enable(self):
        self.is_enabled = True

    async def on_disable(self):
        self.is_enabled = False

    async def on_uninstall(self):
        pass


class InferencePlugin(Plugin):
    pass


class AuthenticationPlugin(Plugin):
    pass


class WebhookPlugin(Plugin):
    pass


class ProviderPlugin(Plugin):
    pass
