from app.plugins.plugin import ProviderPlugin

class CustomProviderPlugin(ProviderPlugin):
    async def on_provider_registered(self, provider_id, *args, **kwargs):
        self.context.logger.info(f"Custom provider registered: {provider_id}")
