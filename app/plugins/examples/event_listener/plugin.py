from app.plugins.plugin import Plugin

class EventListenerPlugin(Plugin):
    async def on_provider_failed(self, provider_id: str):
        if self.context.check_permission("events.publish", "provider.failed"):
            await self.context.publish_event("provider.failed", {"provider_id": provider_id})
