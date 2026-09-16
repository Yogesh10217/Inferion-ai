from app.plugins.plugin import WebhookPlugin


class WebhookLoggerPlugin(WebhookPlugin):
    async def on_webhook_delivered(self, webhook_id, endpoint, *args, **kwargs):
        self.context.logger.info(f"Webhook {webhook_id} delivered to {endpoint}")
