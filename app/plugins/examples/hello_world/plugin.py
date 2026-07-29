from app.plugins.plugin import Plugin

class HelloWorldPlugin(Plugin):
    async def on_initialize(self):
        self.context.logger.info("HelloWorldPlugin initialized")

    async def on_enable(self):
        await super().on_enable()
        self.context.logger.info("HelloWorldPlugin enabled")

    async def on_before_request(self, request_data: dict):
        self.context.logger.info(f"Hello World before request: {request_data}")
        return request_data
