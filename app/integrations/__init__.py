"""Integration Platform Package."""

from app.integrations.agent_integration import AgentIntegrationAdapter
from app.integrations.analytics import IntegrationAnalyticsEngine
from app.integrations.authentication import (
    AuthenticationProfile,
    AuthenticationSession,
    AuthenticationType,
)
from app.integrations.automation import (
    ActionType,
    AutomationDefinition,
    AutomationExecution,
    AutomationManager,
    TriggerType,
)
from app.integrations.billing import IntegrationBillingTracker
from app.integrations.connector import (
    GitHubConnector,
    GitLabConnector,
    IntegrationConnector,
    JiraConnector,
    NotionConnector,
    RESTConnector,
    SlackConnector,
)
from app.integrations.credentials import CredentialBroker, CredentialReference
from app.integrations.events import IntegrationEvent, IntegrationEventRouter
from app.integrations.exceptions import (
    ConnectorExecutionException,
    DuplicateWebhookException,
    IntegrationNotFoundException,
    IntegrationPlatformException,
    PluginSecurityViolationException,
    TransformationException,
    WebhookSignatureException,
)
from app.integrations.governance import IntegrationAccessDecision, IntegrationDecisionType, IntegrationGovernanceEngine
from app.integrations.integration import (
    Integration,
    IntegrationCapability,
    IntegrationConfiguration,
    IntegrationStatus,
    IntegrationType,
    IntegrationVersion,
)
from app.integrations.knowledge_integration import KnowledgeIntegrationAdapter
from app.integrations.manager import IntegrationManager
from app.integrations.marketplace import InstallationRecord, IntegrationMarketplace, MarketplaceListing
from app.integrations.observability import IntegrationMetricsCollector
from app.integrations.plugins import Plugin, PluginManager, PluginManifest, PluginStatus
from app.integrations.registry import IntegrationRegistry
from app.integrations.resilience import (
    IntegrationExecutionState,
    IntegrationExecutionStatus,
    IntegrationResilienceManager,
)
from app.integrations.security import IntegrationSecurityEngine
from app.integrations.transformation import FieldMapping, TransformationPipeline
from app.integrations.webhooks import (
    WebhookDelivery,
    WebhookEndpoint,
    WebhookEvent,
    WebhookManager,
)
from app.integrations.workflow_integration import WorkflowIntegrationAdapter

__all__ = [
    "IntegrationPlatformException",
    "IntegrationNotFoundException",
    "ConnectorExecutionException",
    "WebhookSignatureException",
    "DuplicateWebhookException",
    "PluginSecurityViolationException",
    "TransformationException",
    "Integration",
    "IntegrationVersion",
    "IntegrationCapability",
    "IntegrationConfiguration",
    "IntegrationStatus",
    "IntegrationType",
    "IntegrationRegistry",
    "IntegrationConnector",
    "SlackConnector",
    "GitHubConnector",
    "GitLabConnector",
    "NotionConnector",
    "JiraConnector",
    "RESTConnector",
    "AuthenticationProfile",
    "AuthenticationSession",
    "AuthenticationType",
    "CredentialReference",
    "CredentialBroker",
    "WebhookEndpoint",
    "WebhookEvent",
    "WebhookDelivery",
    "WebhookManager",
    "IntegrationEvent",
    "IntegrationEventRouter",
    "FieldMapping",
    "TransformationPipeline",
    "AutomationDefinition",
    "AutomationExecution",
    "TriggerType",
    "ActionType",
    "AutomationManager",
    "Plugin",
    "PluginManifest",
    "PluginStatus",
    "PluginManager",
    "IntegrationMarketplace",
    "MarketplaceListing",
    "InstallationRecord",
    "IntegrationResilienceManager",
    "IntegrationExecutionState",
    "IntegrationExecutionStatus",
    "IntegrationGovernanceEngine",
    "IntegrationAccessDecision",
    "IntegrationDecisionType",
    "IntegrationSecurityEngine",
    "AgentIntegrationAdapter",
    "WorkflowIntegrationAdapter",
    "KnowledgeIntegrationAdapter",
    "IntegrationAnalyticsEngine",
    "IntegrationMetricsCollector",
    "IntegrationBillingTracker",
    "IntegrationManager",
]
