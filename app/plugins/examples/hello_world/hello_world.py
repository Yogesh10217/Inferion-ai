from app.plugins.plugin import Plugin


class HelloWorldPlugin(Plugin):
    async def on_install(self):
        self.context.logger.info("HelloWorld installed")

    async def on_initialize(self):
        self.context.logger.info("HelloWorld initialized")

    async def on_enable(self):
        await super().on_enable()
        self.context.logger.info("HelloWorld enabled")
