import os

PLUGINS_BASE = r"c:\Users\Yogesh E\OneDrive\Desktop\Manjus\llm-inference-engine\app\plugins\examples"

plugins = {
    "hello_world": """from app.plugins.plugin import Plugin
import logging

class HelloWorldPlugin(Plugin):
    async def on_install(self):
        self.context.logger.info("HelloWorld installed")

    async def on_initialize(self):
        self.context.logger.info("HelloWorld initialized")

    async def on_enable(self):
        await super().on_enable()
        self.context.logger.info("HelloWorld enabled")
""",
    "metrics_logger": """from app.plugins.plugin import Plugin

class MetricsLoggerPlugin(Plugin):
    async def on_system_startup(self, *args, **kwargs):
        self.context.logger.info("System started, logging metrics config")
""",
    "inference_audit": """from app.plugins.plugin import InferencePlugin

class InferenceAuditPlugin(InferencePlugin):
    async def on_inference_request(self, request, *args, **kwargs):
        self.context.logger.info(f"Audit: inference request {request.id}")
        
    async def on_inference_response(self, response, *args, **kwargs):
        self.context.logger.info(f"Audit: inference response {response.id}")
""",
    "webhook_logger": """from app.plugins.plugin import WebhookPlugin

class WebhookLoggerPlugin(WebhookPlugin):
    async def on_webhook_delivered(self, webhook_id, endpoint, *args, **kwargs):
        self.context.logger.info(f"Webhook {webhook_id} delivered to {endpoint}")
""",
    "custom_provider": """from app.plugins.plugin import ProviderPlugin

class CustomProviderPlugin(ProviderPlugin):
    async def on_provider_registered(self, provider_id, *args, **kwargs):
        self.context.logger.info(f"Custom provider registered: {provider_id}")
""",
    "auth_extension": """from app.plugins.plugin import AuthenticationPlugin

class AuthExtensionPlugin(AuthenticationPlugin):
    async def on_authentication_success(self, user_id, *args, **kwargs):
        self.context.logger.info(f"Auth success for user {user_id}")
        
    async def on_authentication_failure(self, user_id, *args, **kwargs):
        self.context.logger.info(f"Auth failure for user {user_id}")
""",
    "event_analytics": """from app.plugins.plugin import Plugin

class EventAnalyticsPlugin(Plugin):
    async def on_event_published(self, event_type, data, *args, **kwargs):
        self.context.logger.info(f"Event analytics tracked: {event_type}")
"""
}

os.makedirs(PLUGINS_BASE, exist_ok=True)
for name, content in plugins.items():
    plugin_dir = os.path.join(PLUGINS_BASE, name)
    os.makedirs(plugin_dir, exist_ok=True)
    with open(os.path.join(plugin_dir, "__init__.py"), "w") as f:
        f.write("")
    with open(os.path.join(plugin_dir, f"{name}.py"), "w") as f:
        f.write(content)

print("Reference plugins created.")
