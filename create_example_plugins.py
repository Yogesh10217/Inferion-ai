import os
import json

EXAMPLES_DIR = r"c:\Users\Yogesh E\OneDrive\Desktop\Manjus\llm-inference-engine\app\plugins\examples"

plugins_data = [
    {
        "dir": "hello_world",
        "manifest": {
            "id": "hello_world",
            "name": "Hello World Plugin",
            "version": "1.0.0",
            "description": "Basic reference plugin demonstrating lifecycle hooks",
            "author": "AGY Team",
            "license": "MIT",
            "entrypoint": "plugin.py:HelloWorldPlugin",
            "minimum_engine_version": "1.0.0",
            "permissions": []
        },
        "code": """from app.plugins.plugin import Plugin

class HelloWorldPlugin(Plugin):
    async def on_initialize(self):
        self.context.logger.info("HelloWorldPlugin initialized")

    async def on_enable(self):
        await super().on_enable()
        self.context.logger.info("HelloWorldPlugin enabled")

    async def on_before_request(self, request_data: dict):
        self.context.logger.info(f"Hello World before request: {request_data}")
        return request_data
"""
    },
    {
        "dir": "metrics_logger",
        "manifest": {
            "id": "metrics_logger",
            "name": "Metrics Logger Plugin",
            "version": "1.0.0",
            "description": "Logs inference metrics on completion",
            "author": "AGY Team",
            "license": "MIT",
            "entrypoint": "plugin.py:MetricsLoggerPlugin",
            "minimum_engine_version": "1.0.0",
            "permissions": []
        },
        "code": """from app.plugins.plugin import Plugin

class MetricsLoggerPlugin(Plugin):
    async def on_after_inference(self, metrics: dict):
        self.context.logger.info(f"Inference metrics logged: {metrics}")
        return metrics
"""
    },
    {
        "dir": "request_logger",
        "manifest": {
            "id": "request_logger",
            "name": "Request Logger Plugin",
            "version": "1.0.0",
            "description": "Logs details of incoming inference requests",
            "author": "AGY Team",
            "license": "MIT",
            "entrypoint": "plugin.py:RequestLoggerPlugin",
            "minimum_engine_version": "1.0.0",
            "permissions": []
        },
        "code": """from app.plugins.plugin import Plugin

class RequestLoggerPlugin(Plugin):
    async def on_before_request(self, request: dict):
        self.context.logger.info(f"Incoming Request: {request.get('model', 'unknown')}")
        return request
"""
    },
    {
        "dir": "audit_logger",
        "manifest": {
            "id": "audit_logger",
            "name": "Audit Logger Plugin",
            "version": "1.0.0",
            "description": "Records audit logs for billing and provider events",
            "author": "AGY Team",
            "license": "MIT",
            "entrypoint": "plugin.py:AuditLoggerPlugin",
            "minimum_engine_version": "1.0.0",
            "permissions": []
        },
        "code": """from app.plugins.plugin import Plugin

class AuditLoggerPlugin(Plugin):
    async def on_provider_selected(self, provider_id: str):
        self.context.logger.info(f"AUDIT: Provider selected -> {provider_id}")
        return provider_id
"""
    },
    {
        "dir": "response_modifier",
        "manifest": {
            "id": "response_modifier",
            "name": "Response Modifier Plugin",
            "version": "1.0.0",
            "description": "Attaches gateway signature to response headers or body",
            "author": "AGY Team",
            "license": "MIT",
            "entrypoint": "plugin.py:ResponseModifierPlugin",
            "minimum_engine_version": "1.0.0",
            "permissions": []
        },
        "code": """from app.plugins.plugin import Plugin

class ResponseModifierPlugin(Plugin):
    async def on_after_request(self, response_data: dict):
        response_data["processed_by_plugin"] = True
        return response_data
"""
    },
    {
        "dir": "health_checker",
        "manifest": {
            "id": "health_checker",
            "name": "Health Checker Plugin",
            "version": "1.0.0",
            "description": "Monitors system health hooks",
            "author": "AGY Team",
            "license": "MIT",
            "entrypoint": "plugin.py:HealthCheckerPlugin",
            "minimum_engine_version": "1.0.0",
            "permissions": []
        },
        "code": """from app.plugins.plugin import Plugin

class HealthCheckerPlugin(Plugin):
    async def on_startup(self):
        self.context.logger.info("HealthChecker plugin started")
"""
    },
    {
        "dir": "event_listener",
        "manifest": {
            "id": "event_listener",
            "name": "Event Listener Plugin",
            "version": "1.0.0",
            "description": "Listens for engine events and publishes telemetry",
            "author": "AGY Team",
            "license": "MIT",
            "entrypoint": "plugin.py:EventListenerPlugin",
            "minimum_engine_version": "1.0.0",
            "permissions": [{"action": "events.publish", "resource": "*"}]
        },
        "code": """from app.plugins.plugin import Plugin

class EventListenerPlugin(Plugin):
    async def on_provider_failed(self, provider_id: str):
        if self.context.check_permission("events.publish", "provider.failed"):
            await self.context.publish_event("provider.failed", {"provider_id": provider_id})
"""
    }
]

for p in plugins_data:
    p_dir = os.path.join(EXAMPLES_DIR, p["dir"])
    os.makedirs(p_dir, exist_ok=True)
    with open(os.path.join(p_dir, "manifest.json"), "w", encoding="utf-8") as f:
        json.dump(p["manifest"], f, indent=2)
    with open(os.path.join(p_dir, "plugin.py"), "w", encoding="utf-8") as f:
        f.write(p["code"])

print("Created 7 example reference plugins.")
