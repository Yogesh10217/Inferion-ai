"""Master Application Platform Manager & Subsystem Orchestrator (Phase 5.22 - Component 16).

Coordinates all 15 application platform sub-managers into a unified application composition and runtime experience layer.
"""

import logging
from typing import Any, Dict, Optional

from app.application_platform.analytics import ApplicationAnalyticsEngine
from app.application_platform.application import ApplicationRegistry
from app.application_platform.billing import ApplicationBillingTracker
from app.application_platform.composition import ApplicationCompositionManager
from app.application_platform.configuration import ConfigurationManager
from app.application_platform.deployment import DeploymentManager
from app.application_platform.features import FeatureManager
from app.application_platform.feedback import FeedbackManager
from app.application_platform.governance import ApplicationGovernanceEngine
from app.application_platform.human_experience import HumanExperienceManager
from app.application_platform.interactions import InteractionManager
from app.application_platform.observability import ApplicationMetricsCollector
from app.application_platform.personalization import PersonalizationEngine
from app.application_platform.repositories import ApplicationRepository, InMemoryApplicationRepository
from app.application_platform.resilience import ApplicationResilienceManager
from app.application_platform.runtime import ApplicationRuntimeManager

logger = logging.getLogger(__name__)


class ApplicationPlatformManager:
    """Master manager orchestrating the Phase 5.22 Enterprise AI Application Platform."""

    def __init__(
        self,
        repository: Optional[ApplicationRepository] = None,
        registry: Optional[ApplicationRegistry] = None,
        composition_manager: Optional[ApplicationCompositionManager] = None,
        deployment_manager: Optional[DeploymentManager] = None,
        runtime_manager: Optional[ApplicationRuntimeManager] = None,
        configuration_manager: Optional[ConfigurationManager] = None,
        feature_manager: Optional[FeatureManager] = None,
        personalization_engine: Optional[PersonalizationEngine] = None,
        interaction_manager: Optional[InteractionManager] = None,
        human_experience_manager: Optional[HumanExperienceManager] = None,
        governance_engine: Optional[ApplicationGovernanceEngine] = None,
        analytics_engine: Optional[ApplicationAnalyticsEngine] = None,
        feedback_manager: Optional[FeedbackManager] = None,
        resilience_manager: Optional[ApplicationResilienceManager] = None,
        metrics_collector: Optional[ApplicationMetricsCollector] = None,
        billing_tracker: Optional[ApplicationBillingTracker] = None,
    ) -> None:
        self.repository = repository or InMemoryApplicationRepository()
        self.registry = registry or ApplicationRegistry(repository=self.repository)
        self.composition_manager = composition_manager or ApplicationCompositionManager()
        self.deployment_manager = deployment_manager or DeploymentManager()
        self.runtime_manager = runtime_manager or ApplicationRuntimeManager()
        self.configuration_manager = configuration_manager or ConfigurationManager()
        self.feature_manager = feature_manager or FeatureManager()
        self.personalization_engine = personalization_engine or PersonalizationEngine()
        self.interaction_manager = interaction_manager or InteractionManager()
        self.human_experience_manager = human_experience_manager or HumanExperienceManager()
        self.governance_engine = governance_engine or ApplicationGovernanceEngine()
        self.analytics_engine = analytics_engine or ApplicationAnalyticsEngine()
        self.feedback_manager = feedback_manager or FeedbackManager()
        self.resilience_manager = resilience_manager or ApplicationResilienceManager()
        self.metrics_collector = metrics_collector or ApplicationMetricsCollector()
        self.billing_tracker = billing_tracker or ApplicationBillingTracker()

        logger.info("[APPLICATION PLATFORM] Master ApplicationPlatformManager initialized successfully.")

    def get_platform_summary(self) -> Dict[str, Any]:
        return {
            "status": "OPERATIONAL",
            "layer": "Application Composition & Runtime Experience",
            "metrics": self.metrics_collector.get_metrics_summary(),
        }
