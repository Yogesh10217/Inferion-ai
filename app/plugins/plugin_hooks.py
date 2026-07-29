from enum import Enum

class PluginHook(str, Enum):
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    INFERENCE_REQUEST = "inference.request"
    INFERENCE_RESPONSE = "inference.response"
    AUTHENTICATION_SUCCESS = "authentication.success"
    AUTHENTICATION_FAILURE = "authentication.failure"
    EVENT_PUBLISHED = "event.published"
    WEBHOOK_DELIVERED = "webhook.delivered"
    BILLING_GENERATED = "billing.generated"
    ORGANIZATION_CREATED = "organization.created"
    PROVIDER_REGISTERED = "provider.registered"
    SCHEDULER_TICK = "scheduler.tick"
