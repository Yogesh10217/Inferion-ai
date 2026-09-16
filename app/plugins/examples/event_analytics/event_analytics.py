from app.plugins.plugin import Plugin


class EventAnalyticsPlugin(Plugin):
    async def on_event_published(self, event_type, data, *args, **kwargs):
        self.context.logger.info(f"Event analytics tracked: {event_type}")
