"""Integration Intelligence Platform Package (Phase 5.40)."""

from app.integration_intelligence.analytics import IntegrationAnalyticsEngine
from app.integration_intelligence.billing import IntegrationBillingTracker
from app.integration_intelligence.compensation import CompensationManager, CompensationPlan, CompensationStatus
from app.integration_intelligence.connectors import (
    ConnectorCapability,
    ConnectorManager,
    ConnectorType,
    IntegrationConnector,
)
from app.integration_intelligence.data_governance import (
    IntegrationDataAssessment,
    IntegrationDataClassification,
    IntegrationDataGovernanceManager,
)
from app.integration_intelligence.dependencies import (
    DependencyImpact,
    IntegrationDependency,
    IntegrationDependencyManager,
)
from app.integration_intelligence.endpoints import EndpointManager, EndpointProtocol, EndpointType, IntegrationEndpoint
from app.integration_intelligence.evidence import IntegrationEvidenceBundle, IntegrationEvidenceManager
from app.integration_intelligence.exceptions import (
    ConnectorAccessDeniedException,
    ConnectorNotFoundException,
    CrossTenantIntegrationAccessException,
    HighRiskIntegrationRequiresApprovalException,
    ImmutableIntegrationRecordException,
    IntegrationDelegationBlockedException,
    IntegrationDependencyException,
    IntegrationExecutionBlockedException,
    IntegrationExecutionNotFoundException,
    IntegrationFailureException,
    IntegrationIntelligenceException,
    IntegrationNotFoundException,
    IntegrationPolicyViolationException,
    IntegrationRetryException,
    IntegrationValidationException,
    WorkflowNotFoundException,
)
from app.integration_intelligence.execution import (
    IntegrationExecution,
    IntegrationExecutionManager,
    IntegrationExecutionStatus,
)
from app.integration_intelligence.failures import (
    FailureSeverity,
    FailureType,
    IntegrationFailure,
    IntegrationFailureManager,
)
from app.integration_intelligence.governance import (
    IntegrationGovernanceDecision,
    IntegrationGovernanceEngine,
    IntegrationGovernanceStatus,
)
from app.integration_intelligence.investigations import (
    IntegrationInvestigation,
    IntegrationInvestigationManager,
    InvestigationStatus,
)
from app.integration_intelligence.learning import IntegrationLearningManager, IntegrationLearningRecord
from app.integration_intelligence.manager import IntegrationIntelligenceManager
from app.integration_intelligence.mapping import (
    IntegrationMapping,
    IntegrationMappingManager,
    MappingRule,
    MappingTransformation,
)
from app.integration_intelligence.observability import IntegrationMetricsCollector
from app.integration_intelligence.orchestration import (
    IntegrationOrchestrationManager,
    IntegrationPlan,
    IntegrationPlanStep,
)
from app.integration_intelligence.recovery import IntegrationRecoveryManager, IntegrationRecoveryPlan, RecoveryStatus
from app.integration_intelligence.retries import RetryDecision, RetryManager, RetryPolicy, RetryStatus
from app.integration_intelligence.risk import (
    IntegrationRiskAssessment,
    IntegrationRiskDimension,
    IntegrationRiskManager,
)
from app.integration_intelligence.routing import IntegrationRoute, IntegrationRoutingManager, RoutingStrategy
from app.integration_intelligence.security import IntegrationSecurityAssessment, IntegrationSecurityManager
from app.integration_intelligence.transactions import (
    IntegrationTransaction,
    TransactionConsistency,
    TransactionCoordinator,
    TransactionState,
)
from app.integration_intelligence.trust import IntegrationTrustDimension, IntegrationTrustEngine
from app.integration_intelligence.verification import (
    IntegrationVerification,
    IntegrationVerificationManager,
    VerificationStatus,
)
from app.integration_intelligence.workflows import (
    IntegrationWorkflow,
    WorkflowManager,
    WorkflowStatus,
    WorkflowTrigger,
    WorkflowType,
)

__all__ = [
    "IntegrationIntelligenceException",
    "CrossTenantIntegrationAccessException",
    "IntegrationNotFoundException",
    "ConnectorNotFoundException",
    "WorkflowNotFoundException",
    "IntegrationExecutionNotFoundException",
    "IntegrationPolicyViolationException",
    "ConnectorAccessDeniedException",
    "IntegrationExecutionBlockedException",
    "IntegrationValidationException",
    "IntegrationFailureException",
    "IntegrationRetryException",
    "IntegrationDelegationBlockedException",
    "ImmutableIntegrationRecordException",
    "HighRiskIntegrationRequiresApprovalException",
    "IntegrationDependencyException",
    "ConnectorManager",
    "ConnectorType",
    "ConnectorCapability",
    "IntegrationConnector",
    "EndpointManager",
    "EndpointType",
    "EndpointProtocol",
    "IntegrationEndpoint",
    "WorkflowManager",
    "WorkflowType",
    "WorkflowTrigger",
    "WorkflowStatus",
    "IntegrationWorkflow",
    "IntegrationMappingManager",
    "MappingRule",
    "MappingTransformation",
    "IntegrationMapping",
    "IntegrationOrchestrationManager",
    "IntegrationPlan",
    "IntegrationPlanStep",
    "IntegrationRoutingManager",
    "RoutingStrategy",
    "IntegrationRoute",
    "IntegrationDependencyManager",
    "DependencyImpact",
    "IntegrationDependency",
    "IntegrationExecutionManager",
    "IntegrationExecutionStatus",
    "IntegrationExecution",
    "RetryManager",
    "RetryPolicy",
    "RetryStatus",
    "RetryDecision",
    "IntegrationFailureManager",
    "FailureType",
    "FailureSeverity",
    "IntegrationFailure",
    "IntegrationRecoveryManager",
    "RecoveryStatus",
    "IntegrationRecoveryPlan",
    "CompensationManager",
    "CompensationStatus",
    "CompensationPlan",
    "TransactionCoordinator",
    "TransactionState",
    "TransactionConsistency",
    "IntegrationTransaction",
    "IntegrationGovernanceEngine",
    "IntegrationGovernanceStatus",
    "IntegrationGovernanceDecision",
    "IntegrationRiskManager",
    "IntegrationRiskDimension",
    "IntegrationRiskAssessment",
    "IntegrationSecurityManager",
    "IntegrationSecurityAssessment",
    "IntegrationDataGovernanceManager",
    "IntegrationDataClassification",
    "IntegrationDataAssessment",
    "IntegrationVerificationManager",
    "VerificationStatus",
    "IntegrationVerification",
    "IntegrationEvidenceManager",
    "IntegrationEvidenceBundle",
    "IntegrationInvestigationManager",
    "InvestigationStatus",
    "IntegrationInvestigation",
    "IntegrationMetricsCollector",
    "IntegrationAnalyticsEngine",
    "IntegrationTrustEngine",
    "IntegrationTrustDimension",
    "IntegrationLearningManager",
    "IntegrationLearningRecord",
    "IntegrationBillingTracker",
    "IntegrationIntelligenceManager",
]
