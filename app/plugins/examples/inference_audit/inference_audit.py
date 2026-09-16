from app.plugins.plugin import InferencePlugin


class InferenceAuditPlugin(InferencePlugin):
    async def on_inference_request(self, request, *args, **kwargs):
        self.context.logger.info(f"Audit: inference request {request.id}")

    async def on_inference_response(self, response, *args, **kwargs):
        self.context.logger.info(f"Audit: inference response {response.id}")
