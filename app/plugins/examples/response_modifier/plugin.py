from app.plugins.plugin import Plugin

class ResponseModifierPlugin(Plugin):
    async def on_after_request(self, response_data: dict):
        response_data["processed_by_plugin"] = True
        return response_data
