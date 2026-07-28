from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class EventDefinition:
    name: str
    version: str
    category: str
    description: str
    schema_reference: Optional[str] = None


class EventRegistry:
    """Registry of all supported event types and their metadata."""

    # Category constants
    CATEGORY_INFERENCE = "inference"
    CATEGORY_TENANT = "tenant"
    CATEGORY_AUTH = "auth"
    CATEGORY_BILLING = "billing"
    CATEGORY_SYSTEM = "system"

    # Event name constants
    INFERENCE_COMPLETED = "inference.completed"
    INFERENCE_FAILED = "inference.failed"
    STREAMING_STARTED = "streaming.started"
    STREAMING_FINISHED = "streaming.finished"

    ORGANIZATION_CREATED = "organization.created"
    ORGANIZATION_SUSPENDED = "organization.suspended"
    WORKSPACE_CREATED = "workspace.created"

    USER_CREATED = "user.created"
    USER_DISABLED = "user.disabled"

    API_KEY_CREATED = "api_key.created"
    API_KEY_REVOKED = "api_key.revoked"

    SUBSCRIPTION_CHANGED = "subscription.changed"
    BUDGET_WARNING = "budget.warning"
    BUDGET_EXCEEDED = "budget.exceeded"
    INVOICE_GENERATED = "invoice.generated"

    PROVIDER_HEALTHY = "provider.healthy"
    PROVIDER_UNHEALTHY = "provider.unhealthy"
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"

    _EVENTS: Dict[str, EventDefinition] = {
        INFERENCE_COMPLETED: EventDefinition(
            name=INFERENCE_COMPLETED,
            version="1.0",
            category=CATEGORY_INFERENCE,
            description="Triggered when an inference request completes successfully.",
            schema_reference="schemas/events/inference_completed_v1.json",
        ),
        INFERENCE_FAILED: EventDefinition(
            name=INFERENCE_FAILED,
            version="1.0",
            category=CATEGORY_INFERENCE,
            description="Triggered when an inference request fails.",
            schema_reference="schemas/events/inference_failed_v1.json",
        ),
        STREAMING_STARTED: EventDefinition(
            name=STREAMING_STARTED,
            version="1.0",
            category=CATEGORY_INFERENCE,
            description="Triggered when SSE streaming response begins.",
            schema_reference="schemas/events/streaming_started_v1.json",
        ),
        STREAMING_FINISHED: EventDefinition(
            name=STREAMING_FINISHED,
            version="1.0",
            category=CATEGORY_INFERENCE,
            description="Triggered when SSE streaming response completes.",
            schema_reference="schemas/events/streaming_finished_v1.json",
        ),
        ORGANIZATION_CREATED: EventDefinition(
            name=ORGANIZATION_CREATED,
            version="1.0",
            category=CATEGORY_TENANT,
            description="Triggered when a new organization is provisioned.",
            schema_reference="schemas/events/organization_created_v1.json",
        ),
        ORGANIZATION_SUSPENDED: EventDefinition(
            name=ORGANIZATION_SUSPENDED,
            version="1.0",
            category=CATEGORY_TENANT,
            description="Triggered when an organization is suspended.",
            schema_reference="schemas/events/organization_suspended_v1.json",
        ),
        WORKSPACE_CREATED: EventDefinition(
            name=WORKSPACE_CREATED,
            version="1.0",
            category=CATEGORY_TENANT,
            description="Triggered when a workspace is created within an organization.",
            schema_reference="schemas/events/workspace_created_v1.json",
        ),
        USER_CREATED: EventDefinition(
            name=USER_CREATED,
            version="1.0",
            category=CATEGORY_AUTH,
            description="Triggered when a new user account is created.",
            schema_reference="schemas/events/user_created_v1.json",
        ),
        USER_DISABLED: EventDefinition(
            name=USER_DISABLED,
            version="1.0",
            category=CATEGORY_AUTH,
            description="Triggered when a user account is disabled.",
            schema_reference="schemas/events/user_disabled_v1.json",
        ),
        API_KEY_CREATED: EventDefinition(
            name=API_KEY_CREATED,
            version="1.0",
            category=CATEGORY_AUTH,
            description="Triggered when an API key is generated.",
            schema_reference="schemas/events/api_key_created_v1.json",
        ),
        API_KEY_REVOKED: EventDefinition(
            name=API_KEY_REVOKED,
            version="1.0",
            category=CATEGORY_AUTH,
            description="Triggered when an API key is revoked.",
            schema_reference="schemas/events/api_key_revoked_v1.json",
        ),
        SUBSCRIPTION_CHANGED: EventDefinition(
            name=SUBSCRIPTION_CHANGED,
            version="1.0",
            category=CATEGORY_BILLING,
            description="Triggered when an organization subscription plan changes.",
            schema_reference="schemas/events/subscription_changed_v1.json",
        ),
        BUDGET_WARNING: EventDefinition(
            name=BUDGET_WARNING,
            version="1.0",
            category=CATEGORY_BILLING,
            description="Triggered when an organization reaches its warning budget threshold.",
            schema_reference="schemas/events/budget_warning_v1.json",
        ),
        BUDGET_EXCEEDED: EventDefinition(
            name=BUDGET_EXCEEDED,
            version="1.0",
            category=CATEGORY_BILLING,
            description="Triggered when an organization reaches its hard budget limit.",
            schema_reference="schemas/events/budget_exceeded_v1.json",
        ),
        INVOICE_GENERATED: EventDefinition(
            name=INVOICE_GENERATED,
            version="1.0",
            category=CATEGORY_BILLING,
            description="Triggered when a new billing invoice is generated.",
            schema_reference="schemas/events/invoice_generated_v1.json",
        ),
        PROVIDER_HEALTHY: EventDefinition(
            name=PROVIDER_HEALTHY,
            version="1.0",
            category=CATEGORY_SYSTEM,
            description="Triggered when an upstream LLM provider health check passes.",
            schema_reference="schemas/events/provider_healthy_v1.json",
        ),
        PROVIDER_UNHEALTHY: EventDefinition(
            name=PROVIDER_UNHEALTHY,
            version="1.0",
            category=CATEGORY_SYSTEM,
            description="Triggered when an upstream LLM provider health check fails.",
            schema_reference="schemas/events/provider_unhealthy_v1.json",
        ),
        SYSTEM_STARTUP: EventDefinition(
            name=SYSTEM_STARTUP,
            version="1.0",
            category=CATEGORY_SYSTEM,
            description="Triggered when the inference engine service starts up.",
            schema_reference="schemas/events/system_startup_v1.json",
        ),
        SYSTEM_SHUTDOWN: EventDefinition(
            name=SYSTEM_SHUTDOWN,
            version="1.0",
            category=CATEGORY_SYSTEM,
            description="Triggered when the inference engine service shuts down.",
            schema_reference="schemas/events/system_shutdown_v1.json",
        ),
    }

    @classmethod
    def get_event(cls, name: str) -> Optional[EventDefinition]:
        return cls._EVENTS.get(name)

    @classmethod
    def is_valid_event(cls, name: str) -> bool:
        return name in cls._EVENTS

    @classmethod
    def list_events(cls, category: Optional[str] = None) -> List[EventDefinition]:
        if category:
            return [e for e in cls._EVENTS.values() if e.category == category]
        return list(cls._EVENTS.values())

    @classmethod
    def list_event_names(cls) -> List[str]:
        return list(cls._EVENTS.keys())
