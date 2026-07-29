from app.plugins.plugin import Plugin

class MetricsLoggerPlugin(Plugin):
    async def on_after_inference(self, metrics: dict):
        self.context.logger.info(f"Inference metrics logged: {metrics}")
        return metrics
