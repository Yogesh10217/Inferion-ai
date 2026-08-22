"""Master IntegrationManager Orchestrator Subsystem."""

import logging
from typing import Dict, Any, Optional, List

from app.integrations.integration import Integration, IntegrationStatus, IntegrationType
from app.integrations.registry import IntegrationRegistry
from app.integrations.credentials import CredentialBroker, CredentialReference
from app.integrations.webhooks import WebhookManager, WebhookEndpoint, WebhookDelivery
from app.integrations.events import IntegrationEventRouter, IntegrationEvent
from app.integrations.transformation import TransformationPipeline, FieldMapping
from app.integrations.automation import AutomationManager, AutomationDefinition, TriggerType, ActionType
from app.integrations.plugins import PluginManager, PluginManifest, Plugin
from app.integrations.marketplace import IntegrationMarketplace
from app.integrations.resilience import IntegrationResilienceManager
from app.integrations.governance import IntegrationGovernanceEngine, IntegrationAccessDecision
from app.integrations.security import IntegrationSecurityEngine
from app.integrations.agent_integration import AgentIntegrationAdapter
from app.integrations.workflow_integration import WorkflowIntegrationAdapter
from app.integrations.knowledge_integration import KnowledgeIntegrationAdapter
from app.integrations.analytics import IntegrationAnalyticsEngine
from app.integrations.observability import IntegrationMetricsCollector
from app.integrations.billing import IntegrationBillingTracker

logger = logging.getLogger(__name__)


class IntegrationManager:
    """Master orchestrator for all Integration, API Connectivity, Event Automation & Ecosystem Platform subsystems."""

    def __init__(self) -> None:
        self.registry = IntegrationRegistry()
        self.credential_broker = CredentialBroker()
        self.webhook_manager = WebhookManager()
        self.event_router = IntegrationEventRouter()
        self.transformation_pipeline = TransformationPipeline()
        self.automation_manager = AutomationManager()
        self.plugin_manager = PluginManager()
        self.marketplace = IntegrationMarketplace()
        self.resilience_manager = IntegrationResilienceManager()
        self.governance_engine = IntegrationGovernanceEngine()
        self.security_engine = IntegrationSecurityEngine()
        self.agent_adapter = AgentIntegrationAdapter()
        self.workflow_adapter = WorkflowIntegrationAdapter()
        self.knowledge_adapter = KnowledgeIntegrationAdapter()
        self.analytics_engine = IntegrationAnalyticsEngine()
        self.metrics_collector = IntegrationMetricsCollector()
        self.billing_tracker = IntegrationBillingTracker()

        logger.info("[INTEGRATION MANAGER] Master IntegrationManager initialized with all integration domain subsystems")

    def register_and_connect_integration(
        self,
        name: str,
        category: IntegrationType = IntegrationType.SAAS,
        tenant_id: str = "global",
        config: Optional[Dict[str, Any]] = None,
    ) -> Integration:
        integ = self.registry.register_integration(name=name, category=category, tenant_id=tenant_id, config=config)
        return integ
