"""Master DeveloperPlatformManager Orchestrator Subsystem."""

import logging
from typing import Dict, Any, Optional, List

from app.developer_platform.developer import DeveloperManager
from app.developer_platform.project import ProjectManager, DeveloperProject
from app.developer_platform.repositories import RepositoryManager, ProjectRepository

from app.developer_platform.api_management import APIManagementEngine, APIService
from app.developer_platform.api_contracts import APIContractValidator, APIContract
from app.developer_platform.api_versions import APIVersionManager
from app.developer_platform.developer_portal import DeveloperPortalManager, DeveloperApplication
from app.developer_platform.sdk_management import SDKManager, SDKArtifact
from app.developer_platform.environments import EnvironmentManager, DevelopmentEnvironment
from app.developer_platform.development_workspaces import WorkspaceManager, DeveloperWorkspace
from app.developer_platform.code_intelligence import CodeIntelligenceEngine
from app.developer_platform.dependency_intelligence import DependencyManager
from app.developer_platform.quality import QualityManager, QualityGate
from app.developer_platform.testing import TestIntelligenceEngine
from app.developer_platform.cicd import PipelineManager, Pipeline
from app.developer_platform.releases import ReleaseManager, SoftwareRelease
from app.developer_platform.deployment_intelligence import DeploymentIntelligenceEngine
from app.developer_platform.change_intelligence import ChangeIntelligenceEngine
from app.developer_platform.developer_assistant import DeveloperAssistantManager
from app.developer_platform.productivity import DeveloperProductivityEngine
from app.developer_platform.analytics import DeveloperAnalyticsEngine
from app.developer_platform.governance import DeveloperGovernanceEngine
from app.developer_platform.observability import DeveloperMetricsCollector
from app.developer_platform.billing import DeveloperBillingAdapter

logger = logging.getLogger(__name__)


class DeveloperPlatformManager:
    """Master orchestrator for Developer Platform, API Management & Software Delivery Intelligence subsystems."""

    def __init__(self) -> None:
        self.developer_manager = DeveloperManager()
        self.project_manager = ProjectManager()
        self.repository_manager = RepositoryManager()

        self.api_management_engine = APIManagementEngine()
        self.contract_validator = APIContractValidator()
        self.version_manager = APIVersionManager()
        self.developer_portal = DeveloperPortalManager()
        self.sdk_manager = SDKManager()
        self.environment_manager = EnvironmentManager()
        self.workspace_manager = WorkspaceManager()
        self.code_intelligence = CodeIntelligenceEngine()
        self.dependency_manager = DependencyManager()
        self.quality_manager = QualityManager()
        self.test_intelligence = TestIntelligenceEngine()
        self.pipeline_manager = PipelineManager()
        self.release_manager = ReleaseManager()
        self.deployment_intelligence = DeploymentIntelligenceEngine()
        self.change_intelligence = ChangeIntelligenceEngine()
        self.developer_assistant = DeveloperAssistantManager()
        self.productivity_engine = DeveloperProductivityEngine()
        self.analytics_engine = DeveloperAnalyticsEngine()
        self.governance_engine = DeveloperGovernanceEngine()
        self.metrics_collector = DeveloperMetricsCollector()
        self.billing_adapter = DeveloperBillingAdapter()

        logger.info("[DEVELOPER PLATFORM MANAGER] Master DeveloperPlatformManager initialized with all 23 software delivery subsystems")

    def create_project_with_repository(
        self,
        name: str,
        description: str = "",
        repo_name: str = "main-repo",
        provider: str = "github",
        tenant_id: str = "global",
    ) -> DeveloperProject:
        proj = self.project_manager.create_project(name=name, description=description, tenant_id=tenant_id)
        repo = self.repository_manager.register_repository(project_id=proj.project_id, name=repo_name, provider=provider, tenant_id=tenant_id)
        proj.repository_ids.append(repo.repository_id)
        return proj
