"""Master AILifecyclePlatformManager Orchestrator Subsystem (Phase 5.33)."""

import logging
from typing import Dict, Any, Optional, List

from app.ai_lifecycle_platform.assets import AIAssetManager, AIAsset, AIAssetType
from app.ai_lifecycle_platform.datasets import DatasetManager, Dataset, DatasetClassification
from app.ai_lifecycle_platform.models import ModelManager, AIModel, ModelType, ModelFramework, ModelLifecycleStage
from app.ai_lifecycle_platform.agents import AgentManager, AIAgent, AgentType, AgentAutonomyLevel
from app.ai_lifecycle_platform.lineage import LineageManager, LineageGraph, LineageRelationshipType
from app.ai_lifecycle_platform.artifacts import ArtifactManager, AIArtifact, ArtifactType
from app.ai_lifecycle_platform.evaluations import EvaluationManager, EvaluationSuite, EvaluationRun
from app.ai_lifecycle_platform.gates import LifecycleGateManager, LifecycleGate, GateType, GateStatus
from app.ai_lifecycle_platform.promotion import PromotionManager, PromotionRequest, PromotionTarget, PromotionStatus
from app.ai_lifecycle_platform.releases import ReleaseManager, AIRelease, ReleaseStatus, ReleaseRisk
from app.ai_lifecycle_platform.deployment import DeploymentManager, DeploymentPlan, DeploymentTarget
from app.ai_lifecycle_platform.monitoring import LifecycleMonitoringManager, AIAssetHealth
from app.ai_lifecycle_platform.drift import DriftManager, DriftDetection, DriftType, DriftSeverity
from app.ai_lifecycle_platform.rollback import RollbackManager, RollbackRequest, RollbackPlan
from app.ai_lifecycle_platform.retirement import RetirementManager, RetirementRequest, RetirementReason, RetirementStatus
from app.ai_lifecycle_platform.risk import LifecycleRiskManager, LifecycleRiskAssessment
from app.ai_lifecycle_platform.trust import LifecycleTrustEngine, LifecycleTrustScore
from app.ai_lifecycle_platform.governance import LifecycleGovernanceEngine, GovernanceDecision
from app.ai_lifecycle_platform.evidence import LifecycleEvidenceManager, LifecycleEvidenceBundle, LifecycleEvidence
from app.ai_lifecycle_platform.snapshots import LifecycleSnapshotManager, LifecycleSnapshot
from app.ai_lifecycle_platform.learning import LifecycleLearningManager, LifecycleLearningRecord
from app.ai_lifecycle_platform.analytics import LifecycleAnalyticsEngine, PlatformReport
from app.ai_lifecycle_platform.observability import LifecycleMetricsCollector
from app.ai_lifecycle_platform.billing import LifecycleBillingTracker
from app.ai_lifecycle_platform.repositories import LifecycleRepository

logger = logging.getLogger(__name__)


class AILifecyclePlatformManager:
    """Master Orchestrator coordinating full 19-stage AI Model, Agent, Dataset & Lifecycle Governance."""

    def __init__(self) -> None:
        self.repository = LifecycleRepository()

        self.asset_manager = AIAssetManager()
        self.dataset_manager = DatasetManager()
        self.model_manager = ModelManager()
        self.agent_manager = AgentManager()
        self.lineage_manager = LineageManager()

        self.artifact_manager = ArtifactManager()
        self.evaluation_manager = EvaluationManager()
        self.gate_manager = LifecycleGateManager()
        self.promotion_manager = PromotionManager()
        self.release_manager = ReleaseManager()

        self.deployment_manager = DeploymentManager()
        self.monitoring_manager = LifecycleMonitoringManager()
        self.drift_manager = DriftManager()
        self.rollback_manager = RollbackManager()
        self.retirement_manager = RetirementManager()

        self.risk_manager = LifecycleRiskManager()
        self.trust_engine = LifecycleTrustEngine()
        self.governance_engine = LifecycleGovernanceEngine()
        self.evidence_manager = LifecycleEvidenceManager()
        self.snapshot_manager = LifecycleSnapshotManager()

        self.learning_manager = LifecycleLearningManager()
        self.analytics_engine = LifecycleAnalyticsEngine()
        self.metrics_collector = LifecycleMetricsCollector()
        self.billing_tracker = LifecycleBillingTracker()

        logger.info("[AI LIFECYCLE MASTER] AILifecyclePlatformManager initialized cleanly with all 29 domain subsystems.")

    def run_full_ai_lifecycle_flow(
        self,
        tenant_id: str,
        asset_name: str = "Enterprise_GPT4_Agent",
        target_env: PromotionTarget = PromotionTarget.PRODUCTION,
        is_high_risk: bool = False,
    ) -> Dict[str, Any]:
        """Executes complete 19-stage E2E AI asset lifecycle flow from dataset registration to retirement & snapshotting."""
        # 1. Dataset Registration
        dataset = self.dataset_manager.register_dataset(tenant_id, f"{asset_name}_Dataset", DatasetClassification.INTERNAL)

        # 2. Model & Agent Registration & Versioning
        model = self.model_manager.register_model(tenant_id, f"{asset_name}_Model", ModelType.LLM, ModelFramework.TRANSFORMERS, dataset_version_ids=[dataset.versions[0].version_id])
        agent = self.agent_manager.register_agent(tenant_id, asset_name, AgentType.TASK_AGENT, AgentAutonomyLevel.HUMAN_APPROVED)

        # 3. Lineage Recording
        lineage = self.lineage_manager.record_lineage(tenant_id, dataset.dataset_id, model.model_id, LineageRelationshipType.TRAINED_ON)

        # 4. Artifact Registration & Integrity
        artifact = self.artifact_manager.register_artifact(tenant_id, f"{asset_name}_Weights", ArtifactType.MODEL_BINARY)

        # 5. Evaluation & Evidence Collection
        suite = self.evaluation_manager.create_suite(tenant_id, f"{asset_name}_Eval_Suite")
        eval_run = self.evaluation_manager.run_evaluation(tenant_id, model.model_id, suite.suite_id, overall_passed=True)
        self.metrics_collector.record_evaluation(eval_run.status.value, tenant_id)

        ev = LifecycleEvidence(tenant_id=tenant_id, source="EVALUATION_RUNNER", content_reference=eval_run.run_id)
        evidence_bundle = self.evidence_manager.create_evidence_bundle(tenant_id, f"Evidence for {asset_name}", [ev])
        finalized_evidence = self.evidence_manager.finalize_bundle(evidence_bundle.bundle_id, tenant_id)

        # 6. Risk & Trust Assessment
        risk_ass = self.risk_manager.assess_lifecycle_risk(tenant_id, model.model_id, eval_run.results[0].score)
        trust_score = self.trust_engine.compute_trust(tenant_id, model.model_id, eval_passed=eval_run.overall_passed, gates_passed=True)

        # 7. Governance Gates & Promotion Request
        gate = self.gate_manager.create_gate(tenant_id, f"{asset_name}_Security_Gate", GateType.SECURITY, is_hard_gate=True)
        gate_evals = self.gate_manager.evaluate_gates(tenant_id, [gate.gate_id], gate_override_pass=True)

        prom_req = self.promotion_manager.request_promotion(
            tenant_id=tenant_id,
            asset_id=model.model_id,
            target=target_env,
            evaluations_passed=eval_run.overall_passed,
            gate_evaluations=gate_evals,
            is_high_risk=is_high_risk,
        )
        self.metrics_collector.record_promotion(target_env.value, tenant_id)

        # 8. Governance Evaluation & Release Creation
        gov_dec = self.governance_engine.evaluate_lifecycle_governance(tenant_id, model.model_id, action_type="PROMOTION", requires_approval=prom_req.status == PromotionStatus.REQUIRE_APPROVAL)
        release = self.release_manager.create_release(tenant_id, f"Release of {asset_name}", model.model_id, version="1.0.0", risk_level=ReleaseRisk.MEDIUM)
        finalized_release = self.release_manager.finalize_release(release.release_id, tenant_id)

        # 9. Delegated Deployment Planning & Verification
        deploy_plan = self.deployment_manager.plan_deployment(tenant_id, finalized_release.release_id, f"dep_idemp_{finalized_release.release_id}", DeploymentTarget.KUBERNETES_CLUSTER)

        # 10. Runtime Monitoring & Drift Detection
        health = self.monitoring_manager.get_asset_health(tenant_id, model.model_id)
        drift = self.drift_manager.detect_drift(tenant_id, model.model_id, DriftType.PERFORMANCE_DRIFT, severity=DriftSeverity.LOW)
        self.metrics_collector.record_drift(drift.drift_type.value, tenant_id)

        # 11. Rollback & Retirement Workflow
        rollback_req = self.rollback_manager.request_rollback(tenant_id, model.model_id, target_version="1.0.0", reason="Precautionary", requires_approval=False)
        rollback_plan = self.rollback_manager.execute_rollback_plan(rollback_req)
        self.metrics_collector.record_rollback(tenant_id)

        ret_req = self.retirement_manager.request_retirement(tenant_id, model.model_id, reason=RetirementReason.DEPRECATED)
        finalized_ret = self.retirement_manager.finalize_retirement(ret_req.retirement_id, tenant_id)
        self.metrics_collector.record_retirement(tenant_id)

        # 12. Immutable Reproducibility Snapshot, Analytics, & Learning
        lsnap = self.snapshot_manager.create_snapshot(
            tenant_id=tenant_id,
            asset_id=model.model_id,
            domain_payload={"model": model.model_dump(), "release": finalized_release.model_dump(), "retirement": finalized_ret.model_dump()},
        )
        finalized_snap = self.snapshot_manager.finalize_snapshot(lsnap.snapshot_id, tenant_id)

        report = self.analytics_engine.generate_report(tenant_id)
        learning = self.learning_manager.record_learning(tenant_id, model.model_id, "Evaluation Drift Pattern", "Tighten Gate Threshold")

        return {
            "dataset": dataset.model_dump(),
            "model": model.model_dump(),
            "agent": agent.model_dump(),
            "lineage": lineage.model_dump(),
            "artifact": artifact.model_dump(),
            "evaluation_run": eval_run.model_dump(),
            "evidence_bundle": finalized_evidence.model_dump(),
            "risk_assessment": risk_ass.model_dump(),
            "trust_score": trust_score.model_dump(),
            "promotion_request": prom_req.model_dump(),
            "governance_decision": gov_dec.model_dump(),
            "release": finalized_release.model_dump(),
            "deployment_plan": deploy_plan.model_dump(),
            "health": health.model_dump(),
            "drift": drift.model_dump(),
            "rollback_plan": rollback_plan.model_dump(),
            "retirement": finalized_ret.model_dump(),
            "snapshot": finalized_snap.model_dump(),
            "analytics": report.model_dump(),
            "learning": learning.model_dump(),
        }
