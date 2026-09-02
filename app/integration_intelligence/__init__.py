"""Integration Intelligence Platform Package (Phase 5.40)."""

from app.integration_intelligence.exceptions import (
    IntegrationIntelligenceException,
    CrossTenantIntegrationAccessException,
    InvalidAccessStateTransitionException,
    IntegrationNotFoundException,
    ConnectorNotFoundException,
    WorkflowNotFoundException,
    IntegrationExecutionNotFoundException,
    IntegrationPolicyViolationException,
    ConnectorAccessDeniedException,
    IntegrationExecutionBlockedException,
    IntegrationValidationException,
    IntegrationFailureException,
    IntegrationRetryException,
    IntegrationDelegationBlockedException,
    ImmutableIntegrationRecordException,
    HighRiskIntegrationRequiresApprovalException,
    IntegrationDependencyException,
)

from app.integration_intelligence.connectors import ConnectorManager, ConnectorType, ConnectorCapability, IntegrationConnector
from app.integration_intelligence.endpoints import EndpointManager, EndpointType, EndpointProtocol, IntegrationEndpoint
from app.integration_intelligence.workflows import WorkflowManager, WorkflowType, WorkflowTrigger, WorkflowStatus, IntegrationWorkflow
from app.integration_intelligence.mapping import IntegrationMappingManager, MappingRule, MappingTransformation, IntegrationMapping
from app.integration_intelligence.orchestration import IntegrationOrchestrationManager, IntegrationPlan, IntegrationPlanStep
from app.integration_intelligence.routing import IntegrationRoutingManager, RoutingStrategy, IntegrationRoute
from app.integration_intelligence.dependencies import IntegrationDependencyManager, DependencyImpact, IntegrationDependency
from app.integration_intelligence.execution import IntegrationExecutionManager, IntegrationExecutionStatus, IntegrationExecution
from app.integration_intelligence.retries import RetryManager, RetryPolicy, RetryStatus, RetryDecision
from app.integration_intelligence.failures import IntegrationFailureManager, FailureType, FailureSeverity, IntegrationFailure
from app.integration_intelligence.recovery import IntegrationRecoveryManager, RecoveryStatus, IntegrationRecoveryPlan
from app.integration_intelligence.compensation import CompensationManager, CompensationStatus, CompensationPlan
from app.integration_intelligence.transactions import TransactionCoordinator, TransactionState, TransactionConsistency, IntegrationTransaction
from app.integration_intelligence.governance import IntegrationGovernanceEngine, IntegrationGovernanceStatus, IntegrationGovernanceDecision
from app.integration_intelligence.risk import IntegrationRiskManager, IntegrationRiskDimension, IntegrationRiskAssessment
from app.integration_intelligence.security import IntegrationSecurityManager, IntegrationSecurityAssessment
from app.integration_intelligence.data_governance import IntegrationDataGovernanceManager, IntegrationDataClassification, IntegrationDataAssessment
from app.integration_intelligence.verification import IntegrationVerificationManager, VerificationStatus, IntegrationVerification
from app.integration_intelligence.evidence import IntegrationEvidenceManager, IntegrationEvidenceBundle
from app.integration_intelligence.investigations import IntegrationInvestigationManager, InvestigationStatus, IntegrationInvestigation
from app.integration_intelligence.observability import IntegrationMetricsCollector
from app.integration_intelligence.analytics import IntegrationAnalyticsEngine
from app.integration_intelligence.trust import IntegrationTrustEngine, IntegrationTrustDimension
from app.integration_intelligence.learning import IntegrationLearningManager, IntegrationLearningRecord
from app.integration_intelligence.billing import IntegrationBillingTracker
from app.integration_intelligence.manager import IntegrationIntelligenceManager

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
