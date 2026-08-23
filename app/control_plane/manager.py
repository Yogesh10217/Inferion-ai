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

        # Phase 5.11 Extensibility Managers
        from app.developer_platform.manager import DeveloperPlatformManager
        from app.extensions.manager import ExtensionManager
        from app.marketplace.manager import MarketplaceManager

        self.developer_platform_manager = DeveloperPlatformManager()
        self.extension_manager = ExtensionManager()
        self.marketplace_manager = MarketplaceManager()

        # Phase 5.12 Data Fabric Manager
        from app.data_fabric.manager import DataFabricManager
        self.data_fabric_manager = DataFabricManager()

        # Phase 5.13 MLOps Manager
        from app.mlops.manager import MLOpsManager
        self.mlops_manager = MLOpsManager()

        # Phase 5.14 FinOps Manager
        from app.finops.manager import FinOpsManager
        self.finops_manager = FinOpsManager()

        # Phase 5.15 Operations Manager
        from app.operations.manager import OperationsManager
        self.operations_manager = OperationsManager()

        # Phase 5.16 Governance Platform Manager
        from app.governance_platform.governance_manager import GovernancePlatformManager
        self.governance_manager = GovernancePlatformManager()

        # Phase 5.17 Identity Security Manager
        from app.identity.manager import IdentitySecurityManager
        self.identity_security_manager = IdentitySecurityManager()

        # Phase 5.18 Orchestration Manager
        from app.orchestration.manager import OrchestrationManager
        from app.knowledge_platform.manager import KnowledgePlatformManager
        from app.integrations.manager import IntegrationManager
        from app.developer_platform.manager import DeveloperPlatformManager
        self.orchestration_manager = OrchestrationManager()
        self.knowledge_platform_manager = KnowledgePlatformManager()
        self.integration_manager = IntegrationManager()
        self.developer_platform_manager = DeveloperPlatformManager()

        # Phase 5.22 Application Platform Manager
        from app.application_platform.manager import ApplicationPlatformManager
        self.application_platform_manager = ApplicationPlatformManager()

        # Phase 5.23 Platform Operations Manager
        from app.platform_operations.manager import PlatformOperationsManager
        self.platform_operations_manager = PlatformOperationsManager()

        # Phase 5.24 Enterprise Intelligence Manager
        from app.intelligence_platform.manager import EnterpriseIntelligenceManager
        self.intelligence_manager = EnterpriseIntelligenceManager()

        # Phase 5.25 Enterprise AI Data Governance Manager
        from app.data_governance.manager import DataGovernanceManager
        self.data_governance_manager = DataGovernanceManager()

        # Phase 5.26 Enterprise AI Architecture Platform Manager
        from app.architecture_platform.manager import ArchitecturePlatformManager
        self.architecture_platform_manager = ArchitecturePlatformManager()

        # Phase 5.27 Enterprise AI Compliance Platform Manager
        from app.compliance_platform.manager import CompliancePlatformManager
        self.compliance_platform_manager = CompliancePlatformManager()

        logger.info("[CONTROL PLANE MASTER] ControlPlaneManager initialized with all platform control subsystems & Phase 5.27 Compliance Platform Manager")















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
