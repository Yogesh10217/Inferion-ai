"""Master Coordinator for MLOps Platform."""

import logging
from typing import Any, Dict

from app.mlops.billing import MLOpsBillingTracker
from app.mlops.deployment import DeploymentManager
from app.mlops.drift import DriftDetector
from app.mlops.evaluation import MLOpsEvaluationEngine
from app.mlops.experiments import ExperimentManager
from app.mlops.governance import MLOpsGovernanceEngine
from app.mlops.model_lifecycle import ModelLifecycleManager
from app.mlops.observability import MLOpsMetricsCollector
from app.mlops.progressive_delivery import ProgressiveDeliveryManager
from app.mlops.prompt_management import PromptManager
from app.mlops.registry import AIAssetRegistry
from app.mlops.releases import ReleaseManager
from app.mlops.rollback import RollbackManager

logger = logging.getLogger(__name__)


class MLOpsManager:
    """Master Coordinator unifying AI Asset Registry, Model Lifecycle, PromptOps, Experiments, Evaluation, Deployments, Progressive Delivery, Releases, Rollbacks, Drift Detection, Governance, Observability, and Billing."""

    def __init__(self) -> None:
        self.registry = AIAssetRegistry()
        self.model_lifecycle = ModelLifecycleManager(registry=self.registry)
        self.prompt_manager = PromptManager(registry=self.registry)
        self.experiments = ExperimentManager()
        self.evaluation_engine = MLOpsEvaluationEngine()
        self.deployment_manager = DeploymentManager(registry=self.registry)
        self.progressive_delivery = ProgressiveDeliveryManager(deployment_manager=self.deployment_manager)
        self.release_manager = ReleaseManager()
        self.rollback_manager = RollbackManager(deployment_manager=self.deployment_manager, registry=self.registry)
        self.drift_detector = DriftDetector(deployment_manager=self.deployment_manager)
        self.governance_engine = MLOpsGovernanceEngine()
        self.metrics_collector = MLOpsMetricsCollector()
        self.billing_tracker = MLOpsBillingTracker()

        logger.info("[MLOPS MANAGER] Master MLOpsManager initialized with all 14 domain subsystems")

    def get_summary(self) -> Dict[str, Any]:
        return {
            "registered_assets": len(self.registry.list_assets()),
            "active_deployments": len(self.deployment_manager.list_deployments()),
            "active_experiments": len(self.experiments._experiments),
            "drift_events_detected": len(self.drift_detector.list_drift_events()),
            "metrics": self.metrics_collector.get_summary(),
        }
