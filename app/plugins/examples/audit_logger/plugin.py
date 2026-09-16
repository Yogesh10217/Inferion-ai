from app.plugins.plugin import Plugin


class AuditLoggerPlugin(Plugin):
    async def on_provider_selected(self, provider_id: str):
        self.context.logger.info(f"AUDIT: Provider selected -> {provider_id}")
        return provider_id
