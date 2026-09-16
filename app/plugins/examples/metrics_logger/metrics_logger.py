from app.plugins.plugin import Plugin


class MetricsLoggerPlugin(Plugin):
    async def on_system_startup(self, *args, **kwargs):
        self.context.logger.info("System started, logging metrics config")
