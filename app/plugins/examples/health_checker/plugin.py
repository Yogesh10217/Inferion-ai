from app.plugins.plugin import Plugin


class HealthCheckerPlugin(Plugin):
    async def on_startup(self):
        self.context.logger.info("HealthChecker plugin started")
