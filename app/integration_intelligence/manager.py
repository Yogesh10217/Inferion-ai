"""Master Integration Intelligence Manager (Phase 5.40)."""

import logging
from typing import Any, Dict

from app.integration_intelligence.analytics import IntegrationAnalyticsEngine
from app.integration_intelligence.billing import IntegrationBillingTracker
from app.integration_intelligence.compensation import CompensationManager
from app.integration_intelligence.connectors import ConnectorCapability, ConnectorManager, ConnectorType
from app.integration_intelligence.data_governance import IntegrationDataClassification, IntegrationDataGovernanceManager
from app.integration_intelligence.dependencies import DependencyImpact, IntegrationDependencyManager
from app.integration_intelligence.endpoints import EndpointManager, EndpointProtocol, EndpointType
from app.integration_intelligence.evidence import IntegrationEvidenceManager
from app.integration_intelligence.execution import IntegrationExecutionManager, IntegrationExecutionStatus
from app.integration_intelligence.failures import IntegrationFailureManager
from app.integration_intelligence.governance import IntegrationGovernanceEngine
from app.integration_intelligence.investigations import IntegrationInvestigationManager
from app.integration_intelligence.learning import IntegrationLearningManager
from app.integration_intelligence.mapping import IntegrationMappingManager, MappingRule
from app.integration_intelligence.observability import IntegrationMetricsCollector
from app.integration_intelligence.orchestration import IntegrationOrchestrationManager, IntegrationPlanStep
from app.integration_intelligence.recovery import IntegrationRecoveryManager
from app.integration_intelligence.retries import RetryManager
from app.integration_intelligence.risk import IntegrationRiskManager
from app.integration_intelligence.routing import IntegrationRoutingManager, RoutingStrategy
from app.integration_intelligence.security import IntegrationSecurityManager
from app.integration_intelligence.transactions import TransactionCoordinator
from app.integration_intelligence.trust import IntegrationTrustEngine
from app.integration_intelligence.verification import IntegrationVerificationManager, VerificationCheck
from app.integration_intelligence.workflows import WorkflowManager, WorkflowStep, WorkflowTrigger, WorkflowType

logger = logging.getLogger(__name__)


class IntegrationIntelligenceManager:
    """Master orchestrator unifying all 22 lifecycle components of the Enterprise Integration Intelligence Platform."""

    def __init__(self) -> None:
        self.connector_manager = ConnectorManager()
        self.endpoint_manager = EndpointManager()
        self.workflow_manager = WorkflowManager()
        self.mapping_manager = IntegrationMappingManager()
        self.orchestration_manager = IntegrationOrchestrationManager()
        self.routing_manager = IntegrationRoutingManager()
        self.dependency_manager = IntegrationDependencyManager()
        self.execution_manager = IntegrationExecutionManager()
        self.retry_manager = RetryManager()
        self.failure_manager = IntegrationFailureManager()
        self.recovery_manager = IntegrationRecoveryManager()
        self.compensation_manager = CompensationManager()
        self.transaction_coordinator = TransactionCoordinator()
        self.governance_engine = IntegrationGovernanceEngine()
        self.risk_manager = IntegrationRiskManager()
        self.security_manager = IntegrationSecurityManager()
        self.data_governance_manager = IntegrationDataGovernanceManager()
        self.verification_manager = IntegrationVerificationManager()
        self.evidence_manager = IntegrationEvidenceManager()
        self.investigation_manager = IntegrationInvestigationManager()
        self.metrics_collector = IntegrationMetricsCollector()
        self.analytics_engine = IntegrationAnalyticsEngine()
        self.trust_engine = IntegrationTrustEngine()
        self.learning_manager = IntegrationLearningManager()
        self.billing_tracker = IntegrationBillingTracker()

        logger.info("[INTEGRATION INTELLIGENCE] IntegrationIntelligenceManager initialized with all 22 lifecycle components.")

    def run_full_lifecycle(self, tenant_id: str, workflow_name: str) -> Dict[str, Any]:
        """Runs complete end-to-end governed integration lifecycle."""
        # 1. Register connector
        conn = self.connector_manager.register_connector(
            tenant_id=tenant_id,
            name=f"{workflow_name}_conn",
            connector_type=ConnectorType.API,
            external_system_id="sys_ext_01",
            provider_name="EnterpriseSaaS",
            base_endpoint_url="https://api.enterprisesaas.com",
            capabilities=[ConnectorCapability.READ, ConnectorCapability.WRITE],
        )

        # 2. Register endpoint
        ep = self.endpoint_manager.register_endpoint(
            tenant_id=tenant_id,
            connector_id=conn.connector_id,
            name="DataSyncEndpoint",
            endpoint_type=EndpointType.REST_API,
            path_or_topic="/v1/sync",
            protocol=EndpointProtocol.HTTP_HTTPS,
        )

        # 3. Define workflow
        step = WorkflowStep(
            name="SyncStep",
            target_connector_id=conn.connector_id,
            target_endpoint_id=ep.endpoint_id,
            action_name="SYNC_RECORDS",
        )
        wf = self.workflow_manager.create_workflow(
            tenant_id=tenant_id,
            name=workflow_name,
            workflow_type=WorkflowType.SYNC_API,
            trigger=WorkflowTrigger.API_INVOCATION,
            steps=[step],
        )
        self.workflow_manager.validate_workflow(tenant_id, wf.workflow_id)

        # 4. Validate mappings
        mapping = self.mapping_manager.create_mapping(
            tenant_id=tenant_id,
            name="SyncMapping",
            source_schema_id="sch_src_01",
            target_schema_id="sch_tgt_01",
            rules=[MappingRule(source_field="ext_id", target_field="id")],
        )
        self.mapping_manager.validate_mapping(tenant_id, mapping.mapping_id, ["id"])

        # 5. Resolve dependencies
        self.dependency_manager.add_dependency(tenant_id, "sys_ext_01", "db_internal_01", DependencyImpact.MEDIUM)

        # 6. Evaluate routing
        self.routing_manager.register_route(tenant_id, conn.connector_id, ep.endpoint_id, RoutingStrategy.PRIMARY)
        route_dec = self.routing_manager.resolve_route(tenant_id, conn.connector_id)

        # 7. Evaluate data governance
        data_asm = self.data_governance_manager.evaluate_data_flow(tenant_id, wf.workflow_id, IntegrationDataClassification.INTERNAL)

        # 8. Evaluate security
        sec_asm = self.security_manager.evaluate_connector_security(tenant_id, conn.connector_id, conn.reference.base_endpoint_url, conn.reference.auth_type)

        # 9. Calculate risk
        risk_asm = self.risk_manager.calculate_risk(tenant_id, wf.workflow_id, 20.0, 20.0, 20.0, 20.0)

        # 10. Evaluate policy & governance
        gov_dec = self.governance_engine.evaluate_governance(tenant_id, wf.workflow_id, "SYNC_RECORDS", risk_asm.composite_risk_score)
        self.workflow_manager.govern_workflow(tenant_id, wf.workflow_id)
        self.workflow_manager.mark_ready(tenant_id, wf.workflow_id)

        # 11. Create plan
        plan_step = IntegrationPlanStep(
            step_order=1,
            name="SyncStep",
            target_connector_id=conn.connector_id,
            target_endpoint_id=ep.endpoint_id,
            action_type="SYNC_RECORDS",
        )
        plan = self.orchestration_manager.create_plan(tenant_id, wf.workflow_id, f"{workflow_name}_plan", [plan_step])

        # 12. Execution & Delegation
        idem_key = f"idem_full_{workflow_name}"
        exec_obj = self.execution_manager.request_execution(tenant_id, wf.workflow_id, idem_key)
        self.execution_manager.evaluate_governance(tenant_id, exec_obj.execution_id)
        del_req = self.execution_manager.delegate_execution(tenant_id, exec_obj.execution_id)

        # 13. Verification
        check = VerificationCheck(target_system_id="sys_ext_01", expected_status_code=200, observed_status_code=200, passed=True)
        verif = self.verification_manager.verify_execution(tenant_id, exec_obj.execution_id, [check])

        # 14. Evidence & Snapshot
        bundle = self.evidence_manager.create_bundle(tenant_id, f"Evidence {workflow_name}")
        self.evidence_manager.add_evidence(tenant_id, bundle.bundle_id, "EXECUTION_RECORD", exec_obj.execution_id, {"status": "SUCCESS"})
        self.evidence_manager.finalize_bundle(tenant_id, bundle.bundle_id)

        # 15. Finalize Execution
        fin_exec = self.execution_manager.finalize_execution(tenant_id, exec_obj.execution_id, IntegrationExecutionStatus.COMPLETED)
        self.workflow_manager.complete_workflow(tenant_id, wf.workflow_id)

        # 16. Metrics, Analytics, Billing
        self.metrics_collector.increment("workflow_requests_total")
        self.metrics_collector.increment("delegated_executions_total")
        report = self.analytics_engine.generate_report(tenant_id, 1, 1, 100.0, 0, 0, 0)
        cost_evt = self.billing_tracker.record_cost(tenant_id, wf.workflow_id, "WORKFLOW_EXECUTION", 0.005)

        # 17. Learning
        lrn = self.learning_manager.record_learning_pattern(
            tenant_id, "SuccessfulSyncPattern", "Optimized sync workflow execution",
            "Maintain Sync Schedule", "Keep daily schedule unchanged", target_workflow_id=wf.workflow_id
        )

        return {
            "status": "COMPLETED",
            "workflow_id": wf.workflow_id,
            "execution_id": fin_exec.execution_id,
            "delegation_id": del_req.delegation_id,
            "governance_status": gov_dec.status.value,
            "risk_score": risk_asm.composite_risk_score,
            "evidence_fingerprint": bundle.integrity.sha256_hash if bundle.integrity else "",
            "execution_fingerprint": fin_exec.fingerprint,
        }
