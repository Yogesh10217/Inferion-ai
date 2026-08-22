"""Master Control Plane Manager unifying platform administration & subsystem governance."""

import logging
from typing import Dict, Any, Optional

from app.control_plane.tenant import TenantManager
from app.control_plane.organization import OrganizationManager
from app.control_plane.workspace import WorkspaceManager
from app.control_plane.resource_registry import ResourceRegistry
from app.control_plane.resource_graph import ResourceGraph
from app.control_plane.configuration import ConfigurationManager
from app.control_plane.configuration_validator import ControlPlaneConfigurationValidator
from app.control_plane.feature_management import FeatureManager
from app.control_plane.feature_evaluation import FeatureEvaluator
from app.control_plane.policy_manager import PolicyManager
from app.control_plane.policy_simulator import PolicySimulator
from app.control_plane.admin_manager import AdminManager
from app.control_plane.admin_operations import AdminOperationsManager
from app.control_plane.lifecycle_manager import LifecycleManager
from app.control_plane.provisioning import ProvisioningEngine
from app.control_plane.usage_manager import ControlPlaneUsageManager
from app.control_plane.usage_analytics import ControlPlaneUsageAnalytics
from app.control_plane.admin_audit import AdministrativeAuditLedger
from app.control_plane.change_history import ChangeHistoryTracker
from app.control_plane.control_plane_metrics import ControlPlaneMetricsCollector

logger = logging.getLogger(__name__)


class ControlPlaneManager:
    """Master Control Plane Manager orchestrating all 18 platform management subsystems."""

    def __init__(self) -> None:
        self.tenant_manager = TenantManager()
        self.organization_manager = OrganizationManager()
        self.workspace_manager = WorkspaceManager()

        self.resource_registry = ResourceRegistry()
        self.resource_graph = ResourceGraph()

        self.configuration_manager = ConfigurationManager()
        self.configuration_validator = ControlPlaneConfigurationValidator()

        self.feature_manager = FeatureManager()
        self.feature_evaluator = FeatureEvaluator(manager=self.feature_manager)

        self.policy_manager = PolicyManager()
        self.policy_simulator = PolicySimulator(
            policy_manager=self.policy_manager,
            resource_registry=self.resource_registry,
        )

        self.admin_manager = AdminManager(
            tenant_manager=self.tenant_manager,
            organization_manager=self.organization_manager,
            workspace_manager=self.workspace_manager,
        )
        self.admin_operations = AdminOperationsManager()

        self.lifecycle_manager = LifecycleManager()
        self.provisioning_engine = ProvisioningEngine(
            tenant_manager=self.tenant_manager,
            organization_manager=self.organization_manager,
            workspace_manager=self.workspace_manager,
        )

        self.usage_manager = ControlPlaneUsageManager()
        self.usage_analytics = ControlPlaneUsageAnalytics(usage_manager=self.usage_manager)

        self.audit_ledger = AdministrativeAuditLedger()
        self.change_history = ChangeHistoryTracker()
        self.metrics_collector = ControlPlaneMetricsCollector()

        logger.info("[CONTROL PLANE MASTER] ControlPlaneManager initialized with all 18 platform control subsystems")

    def get_summary(self) -> Dict[str, Any]:
        """Aggregate master control plane status summary."""
        self.metrics_collector.increment("control_plane_requests_total")
        overview = self.admin_manager.get_platform_overview()
        metrics = self.metrics_collector.get_metrics_summary()

        return {
            "status": "OPERATIONAL",
            "overview": overview,
            "metrics": metrics,
            "emergency_stop_active": self.admin_operations.emergency_stop_active,
        }
