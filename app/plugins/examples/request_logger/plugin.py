from app.plugins.plugin import Plugin


class RequestLoggerPlugin(Plugin):
    async def on_before_request(self, request: dict):
        self.context.logger.info(f"Incoming Request: {request.get('model', 'unknown')}")
        return request
