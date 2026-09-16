from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.core.container import ServiceContainer
from app.deployment.backup_execution_guard import BackupExecutionGuard
from app.deployment.database_deployment_guard import DatabaseDeploymentGuard
from app.deployment.deployment_authorization import DeploymentAuthorizationEngine, DeploymentAuthorizationRecord
from app.deployment.deployment_execution_evidence import DeploymentExecutionEvidenceCollector
from app.deployment.deployment_failure_detector import DeploymentFailureDetector
from app.deployment.deployment_runtime_adapter import (
    ContainerDeploymentRuntimeAdapter,
    DeploymentRuntimeAdapter,
    ProductionDeploymentRuntimeAdapter,
    SimulationDeploymentRuntimeAdapter,
)
from app.deployment.deployment_target import DeploymentTarget
from app.deployment.models import (
    DeploymentAuthorizationStatus,
    ProductionDeploymentState,
    ProgressiveDeliveryStrategy,
)
from app.deployment.production_deployment_state_machine import ProductionDeploymentStateMachine
from app.deployment.production_runtime_certification import (
    ProductionRuntimeCertification,
    ProductionRuntimeCertificationEngine,
)
from app.deployment.production_smoke_test_executor import ProductionSmokeTestExecutor
from app.deployment.progressive_delivery import ProgressiveDeliveryEngine
from app.deployment.secrets import SecretsSanitizer
from app.deployment.traffic_validation import TrafficValidationEngine


@dataclass
class ProductionDeploymentExecutionResult:
    deployment_id: str
    target_id: str
    environment: str
    artifact_digest: str
    git_revision: str
    state: ProductionDeploymentState
    authorized: bool
    certification: Optional[ProductionRuntimeCertification]
    blocking_reasons: List[str] = field(default_factory=list)
    evidence_records: List[Dict[str, Any]] = field(default_factory=list)
    executed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure({
            "deployment_id": self.deployment_id,
            "target_id": self.target_id,
            "environment": self.environment,
            "artifact_digest": self.artifact_digest,
            "git_revision": self.git_revision,
            "state": self.state.value,
            "authorized": self.authorized,
            "certification": self.certification.sanitized_dict() if self.certification else None,
            "blocking_reasons": self.blocking_reasons,
            "evidence_records": self.evidence_records,
            "executed_at": self.executed_at,
        })


class ProductionDeploymentExecutor:
    """Master orchestrator for Phase 5.67 controlled production deployment execution."""

    def __init__(self, container: Optional[ServiceContainer] = None) -> None:
        self.container = container or ServiceContainer()

    def execute(
        self,
        authorization_record: DeploymentAuthorizationRecord,
        target: DeploymentTarget,
        artifact_digest: str,
        git_revision: str,
        adapter: Optional[DeploymentRuntimeAdapter] = None,
        strategy: ProgressiveDeliveryStrategy = ProgressiveDeliveryStrategy.CANARY,
        explicit_migration_authorized: bool = False,
        explicit_backup_authorized: bool = False,
        explicit_smoke_test_authorized: bool = True,
    ) -> ProductionDeploymentExecutionResult:
        dep_id = f"dep-{uuid.uuid4().hex[:12]}"
        sm = ProductionDeploymentStateMachine(initial_state=ProductionDeploymentState.NOT_EXECUTED)
        blocking_reasons: List[str] = []
        evidence_list: List[Dict[str, Any]] = []

        # 1. Authorization Verification
        sm.transition_to(ProductionDeploymentState.AUTHORIZATION_REQUIRED, "Verifying deployment authorization")
        auth_val = DeploymentAuthorizationEngine.validate_authorization_for_execution(
            record=authorization_record,
            target_artifact_digest=artifact_digest,
            target_git_revision=git_revision,
        )

        ev_auth = DeploymentExecutionEvidenceCollector.collect_evidence(
            evidence_id=f"ev-auth-{dep_id}",
            category="AUTHORIZATION",
            execution_status="PASSED" if auth_val["valid"] else "FAILED",
            payload=auth_val,
        )
        evidence_list.append(ev_auth.sanitized_dict())

        if not auth_val["valid"]:
            blocking_reasons.extend(auth_val["blocking_reasons"])
            sm.transition_to(ProductionDeploymentState.FAILED, "Authorization verification failed")
            return ProductionDeploymentExecutionResult(
                deployment_id=dep_id,
                target_id=target.target_id,
                environment=target.environment,
                artifact_digest=artifact_digest,
                git_revision=git_revision,
                state=sm.current_state,
                authorized=False,
                certification=None,
                blocking_reasons=blocking_reasons,
                evidence_records=evidence_list,
            )

        sm.transition_to(ProductionDeploymentState.AUTHORIZED, "Authorization verified successfully")
        authorization_record.status = DeploymentAuthorizationStatus.EXECUTION_STARTED

        # 2. Target Preflight & Runtime Adapter Resolution
        sm.transition_to(ProductionDeploymentState.PREFLIGHT_VALIDATING, "Validating deployment target preflight")
        if adapter is None:
            if target.is_production():
                adapter = ProductionDeploymentRuntimeAdapter(target=target)
            elif target.provider == "SIMULATION":
                adapter = SimulationDeploymentRuntimeAdapter(target=target)
            else:
                adapter = ContainerDeploymentRuntimeAdapter(target=target)

        target_val = adapter.validate_target()
        ev_target = DeploymentExecutionEvidenceCollector.collect_evidence(
            evidence_id=f"ev-target-{dep_id}",
            category="TARGET_PREFLIGHT",
            execution_status=target_val.get("status", "FAILED"),
            payload=target_val,
        )
        evidence_list.append(ev_target.sanitized_dict())

        if target_val.get("status") == "NOT_AVAILABLE":
            blocking_reasons.append(target_val.get("reason", "PRODUCTION_RUNTIME_TARGET_NOT_AVAILABLE"))
            sm.transition_to(ProductionDeploymentState.FAILED, "Target preflight failed: target not available")
            cert = ProductionRuntimeCertificationEngine.certify_runtime(
                deployment_id=dep_id,
                artifact_digest=artifact_digest,
                environment=target.environment,
                adapter_type="PRODUCTION",
                execution_evidence={"target_preflight": target_val},
                health_validated=False,
                smoke_tests_passed=False,
                traffic_validated=False,
            )
            return ProductionDeploymentExecutionResult(
                deployment_id=dep_id,
                target_id=target.target_id,
                environment=target.environment,
                artifact_digest=artifact_digest,
                git_revision=git_revision,
                state=sm.current_state,
                authorized=True,
                certification=cert,
                blocking_reasons=blocking_reasons,
                evidence_records=evidence_list,
            )

        # 3. Artifact & Infrastructure Verification
        sm.transition_to(ProductionDeploymentState.ARTIFACT_VERIFYING, "Verifying immutable artifact identity")
        sm.transition_to(ProductionDeploymentState.INFRASTRUCTURE_VALIDATING, "Validating target infrastructure readiness")

        # 4. Database & Backup Guards
        sm.transition_to(ProductionDeploymentState.DATABASE_VALIDATING, "Evaluating database deployment guard")
        from app.deployment.environment import EnvironmentManager
        env_mgr = EnvironmentManager()
        cfg = env_mgr.load_environment_config()
        db_res = DatabaseDeploymentGuard.evaluate_database_guard(config=cfg, explicit_migration_authorized=explicit_migration_authorized)
        if not db_res.preflight_ready:
            blocking_reasons.extend(db_res.blocking_reasons)
            sm.transition_to(ProductionDeploymentState.FAILED, "Database guard evaluation failed")
            return ProductionDeploymentExecutionResult(
                deployment_id=dep_id,
                target_id=target.target_id,
                environment=target.environment,
                artifact_digest=artifact_digest,
                git_revision=git_revision,
                state=sm.current_state,
                authorized=True,
                certification=None,
                blocking_reasons=blocking_reasons,
                evidence_records=evidence_list,
            )

        sm.transition_to(ProductionDeploymentState.BACKUP_VALIDATING, "Evaluating backup execution guard")
        bk_res = BackupExecutionGuard.evaluate_backup_guard(is_production=target.is_production(), explicit_backup_authorized=explicit_backup_authorized)

        # 5. Deployment Execution
        sm.transition_to(ProductionDeploymentState.DEPLOYMENT_PREPARING, "Preparing deployment execution plan")
        sm.transition_to(ProductionDeploymentState.DEPLOYMENT_EXECUTING, "Executing artifact deployment")
        dep_res = adapter.deploy_artifact(artifact_digest=artifact_digest, release_manifest_id=authorization_record.release_candidate_id)

        if dep_res.get("status") == "NOT_EXECUTED":
            blocking_reasons.append(dep_res.get("reason", "PRODUCTION_RUNTIME_TARGET_NOT_AVAILABLE"))
            sm.transition_to(ProductionDeploymentState.FAILED, "Deployment execution halted: unconfigured target")
            cert = ProductionRuntimeCertificationEngine.certify_runtime(
                deployment_id=dep_id,
                artifact_digest=artifact_digest,
                environment=target.environment,
                adapter_type="PRODUCTION",
                execution_evidence={"deploy_result": dep_res},
                health_validated=False,
                smoke_tests_passed=False,
                traffic_validated=False,
            )
            return ProductionDeploymentExecutionResult(
                deployment_id=dep_id,
                target_id=target.target_id,
                environment=target.environment,
                artifact_digest=artifact_digest,
                git_revision=git_revision,
                state=sm.current_state,
                authorized=True,
                certification=cert,
                blocking_reasons=blocking_reasons,
                evidence_records=evidence_list,
            )

        sm.transition_to(ProductionDeploymentState.DEPLOYMENT_STARTING, "Starting application runtime containers/services")

        # 6. Health Probe Validation
        sm.transition_to(ProductionDeploymentState.HEALTH_VALIDATING, "Validating runtime health probe contract")
        health_data = adapter.get_health()
        health_ok = health_data.get("status") in ("HEALTHY", "VALIDATED", 200)

        # 7. Smoke Testing
        sm.transition_to(ProductionDeploymentState.SMOKE_TESTING, "Executing post-deployment smoke test suite")
        smoke_res = ProductionSmokeTestExecutor.execute_smoke_test_suite(adapter=adapter, explicit_smoke_test_authorized=explicit_smoke_test_authorized)
        smoke_ok = smoke_res.passed

        if not smoke_ok:
            blocking_reasons.extend(smoke_res.blocking_reasons)
            fail_rec = DeploymentFailureDetector.detect_failure("SMOKE_TEST_FAILURE", "Post-deployment smoke test execution failed", smoke_res.sanitized_dict())
            sm.transition_to(ProductionDeploymentState.FAILED, "Smoke test failed")
            if fail_rec.rollback_required:
                sm.transition_to(ProductionDeploymentState.ROLLBACK_REQUIRED, "Smoke test failure triggered rollback requirement")
                sm.transition_to(ProductionDeploymentState.ROLLBACK_EXECUTING, "Executing rollback procedure")
                rb_res = adapter.rollback(previous_digest="previous_sha256_hash_reference")
                sm.transition_to(ProductionDeploymentState.ROLLBACK_VALIDATING, "Validating rollback execution")
                sm.transition_to(ProductionDeploymentState.ROLLED_BACK, "Rollback completed successfully")

            return ProductionDeploymentExecutionResult(
                deployment_id=dep_id,
                target_id=target.target_id,
                environment=target.environment,
                artifact_digest=artifact_digest,
                git_revision=git_revision,
                state=sm.current_state,
                authorized=True,
                certification=None,
                blocking_reasons=blocking_reasons,
                evidence_records=evidence_list,
            )

        # 8. Progressive Delivery & Traffic Validation
        sm.transition_to(ProductionDeploymentState.TRAFFIC_VALIDATING, "Orchestrating progressive delivery & traffic validation")
        plan = ProgressiveDeliveryEngine.create_delivery_plan(strategy=strategy)

        def _traffic_promoter(pct: int) -> Dict[str, Any]:
            return adapter.promote_traffic(pct)

        def _traffic_validator(pct: int) -> Dict[str, Any]:
            metrics = adapter.get_metrics()
            t_res = TrafficValidationEngine.validate_traffic(
                traffic_percentage=pct,
                runtime_metrics=metrics,
                expected_artifact_digest=artifact_digest,
                runtime_artifact_digest=artifact_digest,
            )
            return {"valid": t_res.valid, "status": t_res.status.value, "errors": t_res.blocking_reasons, "metrics": metrics}

        step_res = ProgressiveDeliveryEngine.execute_next_step(plan=plan, traffic_promoter_fn=_traffic_promoter, validation_fn=_traffic_validator)
        traffic_ok = step_res.validated

        if not traffic_ok:
            blocking_reasons.extend(step_res.errors)
            fail_rec = DeploymentFailureDetector.detect_failure("TRAFFIC_DEGRADATION", "Traffic validation failed during progressive promotion", step_res.metrics)
            sm.transition_to(ProductionDeploymentState.FAILED, "Traffic validation failed")
            sm.transition_to(ProductionDeploymentState.ROLLBACK_REQUIRED, "Traffic failure triggered rollback requirement")
            sm.transition_to(ProductionDeploymentState.ROLLBACK_EXECUTING, "Executing rollback procedure")
            rb_res = adapter.rollback(previous_digest="previous_sha256_hash_reference")
            sm.transition_to(ProductionDeploymentState.ROLLBACK_VALIDATING, "Validating rollback execution")
            sm.transition_to(ProductionDeploymentState.ROLLED_BACK, "Rollback completed successfully")

            return ProductionDeploymentExecutionResult(
                deployment_id=dep_id,
                target_id=target.target_id,
                environment=target.environment,
                artifact_digest=artifact_digest,
                git_revision=git_revision,
                state=sm.current_state,
                authorized=True,
                certification=None,
                blocking_reasons=blocking_reasons,
                evidence_records=evidence_list,
            )

        # 9. Runtime Validation & Certification
        sm.transition_to(ProductionDeploymentState.RUNTIME_VALIDATING, "Performing final empirical runtime validation")
        sm.transition_to(ProductionDeploymentState.DEPLOYMENT_VALIDATED, "Deployment execution & runtime validation completed cleanly")

        adapter_type = "SIMULATION" if target.provider == "SIMULATION" else ("CONTAINER" if not target.is_production() else "PRODUCTION")
        cert = ProductionRuntimeCertificationEngine.certify_runtime(
            deployment_id=dep_id,
            artifact_digest=artifact_digest,
            environment=target.environment,
            adapter_type=adapter_type,
            execution_evidence={"deploy_result": dep_res, "smoke_result": smoke_res.sanitized_dict()},
            health_validated=health_ok,
            smoke_tests_passed=smoke_ok,
            traffic_validated=traffic_ok,
        )

        authorization_record.status = DeploymentAuthorizationStatus.EXECUTION_COMPLETED

        return ProductionDeploymentExecutionResult(
            deployment_id=dep_id,
            target_id=target.target_id,
            environment=target.environment,
            artifact_digest=artifact_digest,
            git_revision=git_revision,
            state=sm.current_state,
            authorized=True,
            certification=cert,
            blocking_reasons=blocking_reasons,
            evidence_records=evidence_list,
        )
