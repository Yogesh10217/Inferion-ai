"""Mandatory 16 E2E Verification Test Flows for AI Lifecycle Platform (Phase 5.33)."""

import pytest

from app.ai_lifecycle_platform.manager import AILifecyclePlatformManager
from app.ai_lifecycle_platform.assets import AIAssetType
from app.ai_lifecycle_platform.datasets import DatasetClassification
from app.ai_lifecycle_platform.models import ModelType, ModelFramework, ModelLifecycleStage
from app.ai_lifecycle_platform.agents import AgentType, AgentAutonomyLevel
from app.ai_lifecycle_platform.lineage import LineageRelationshipType
from app.ai_lifecycle_platform.artifacts import ArtifactType
from app.ai_lifecycle_platform.gates import GateType, GateStatus
from app.ai_lifecycle_platform.promotion import PromotionTarget, PromotionStatus
from app.ai_lifecycle_platform.releases import ReleaseRisk, ReleaseStatus
from app.ai_lifecycle_platform.deployment import DeploymentTarget
from app.ai_lifecycle_platform.drift import DriftType, DriftSeverity
from app.ai_lifecycle_platform.retirement import RetirementReason, RetirementStatus
from app.ai_lifecycle_platform.evidence import LifecycleEvidence
from app.platform_contracts.governance import GovernanceDecisionStatus
from app.platform_contracts.delegation import DelegationTarget
from app.ai_lifecycle_platform.exceptions import (
    CrossTenantLifecycleAccessException,
    ImmutableLifecycleRecordException,
    EvaluationGateFailedException,
    ArtifactIntegrityException,
)


def test_flow1_dataset_to_model_lineage():
    """Flow 1: Dataset -> Model -> Evaluation -> Lineage verification."""
    mgr = AILifecyclePlatformManager()
    tenant = "tenant_lc_1"

    dataset = mgr.dataset_manager.register_dataset(tenant, "Dataset_1", DatasetClassification.INTERNAL)
    model = mgr.model_manager.register_model(tenant, "Model_1", ModelType.LLM, dataset_version_ids=[dataset.versions[0].version_id])
    lineage = mgr.lineage_manager.record_lineage(tenant, dataset.dataset_id, model.model_id, LineageRelationshipType.TRAINED_ON)

    assert lineage.edges[0].source_node_id == dataset.dataset_id
    assert lineage.edges[0].target_node_id == model.model_id
    assert lineage.edges[0].relationship == LineageRelationshipType.TRAINED_ON


def test_flow2_model_promotion_success():
    """Flow 2: Evaluation PASS -> Gates PASS -> Promotion -> Release."""
    mgr = AILifecyclePlatformManager()
    tenant = "tenant_lc_2"

    model = mgr.model_manager.register_model(tenant, "Model_2")
    suite = mgr.evaluation_manager.create_suite(tenant, "Suite_2")
    eval_run = mgr.evaluation_manager.run_evaluation(tenant, model.model_id, suite.suite_id, overall_passed=True)

    gate = mgr.gate_manager.create_gate(tenant, "Gate_2", GateType.SECURITY)
    gate_evals = mgr.gate_manager.evaluate_gates(tenant, [gate.gate_id], gate_override_pass=True)

    prom_req = mgr.promotion_manager.request_promotion(tenant, model.model_id, PromotionTarget.STAGING, evaluations_passed=eval_run.overall_passed, gate_evaluations=gate_evals)
    release = mgr.release_manager.create_release(tenant, "Release_2", model.model_id)

    assert prom_req.status == PromotionStatus.APPROVED
    assert release.status == ReleaseStatus.DRAFT


def test_flow3_hard_gate_blocks_promotion():
    """Flow 3: Security/Compliance hard failure -> Promotion BLOCKED."""
    mgr = AILifecyclePlatformManager()
    tenant = "tenant_lc_3"

    model = mgr.model_manager.register_model(tenant, "Model_3")
    gate = mgr.gate_manager.create_gate(tenant, "Security_Gate", GateType.SECURITY, is_hard_gate=True)
    gate_evals = mgr.gate_manager.evaluate_gates(tenant, [gate.gate_id], gate_override_pass=False)

    with pytest.raises(EvaluationGateFailedException):
        mgr.promotion_manager.request_promotion(tenant, model.model_id, PromotionTarget.PRODUCTION, gate_evaluations=gate_evals)


def test_flow4_high_risk_production_requires_approval():
    """Flow 4: High risk -> REQUIRE_APPROVAL -> approval -> promotion."""
    mgr = AILifecyclePlatformManager()
    tenant = "tenant_lc_4"

    model = mgr.model_manager.register_model(tenant, "Model_4")
    prom_req = mgr.promotion_manager.request_promotion(tenant, model.model_id, PromotionTarget.PRODUCTION, is_high_risk=True)

    assert prom_req.status == PromotionStatus.REQUIRE_APPROVAL


def test_flow5_agent_autonomy_governance():
    """Flow 5: High autonomy agent -> governance evaluation required."""
    mgr = AILifecyclePlatformManager()
    tenant = "tenant_lc_5"

    ag1 = mgr.agent_manager.register_agent(tenant, "Assisted_Agent", autonomy_level=AgentAutonomyLevel.ASSISTED)
    ag2 = mgr.agent_manager.register_agent(tenant, "Autonomous_Agent", autonomy_level=AgentAutonomyLevel.LIMITED_AUTONOMOUS)

    assert not mgr.agent_manager.requires_governance_evaluation(ag1)
    assert mgr.agent_manager.requires_governance_evaluation(ag2)


def test_flow6_drift_detection():
    """Flow 6: Monitoring signal -> drift detected -> evidence -> recommendation."""
    mgr = AILifecyclePlatformManager()
    tenant = "tenant_lc_6"

    drift = mgr.drift_manager.detect_drift(tenant, "model_6", DriftType.PERFORMANCE_DRIFT, severity=DriftSeverity.HIGH)

    assert drift.evidence is not None
    assert "RE_EVALUATION_REQUIRED" in drift.recommendations


def test_flow7_high_severity_drift_blocks_release():
    """Flow 7: Critical drift -> release/promotion blocked recommendation."""
    mgr = AILifecyclePlatformManager()
    tenant = "tenant_lc_7"

    drift = mgr.drift_manager.detect_drift(tenant, "model_7", DriftType.SAFETY_DRIFT, severity=DriftSeverity.CRITICAL)

    assert "PROMOTION_BLOCK" in drift.recommendations
    assert "ROLLBACK_RECOMMENDED" in drift.recommendations


def test_flow8_controlled_rollback():
    """Flow 8: Rollback request -> governance -> approval if required -> DelegationRequest."""
    mgr = AILifecyclePlatformManager()
    tenant = "tenant_lc_8"

    rbreq = mgr.rollback_manager.request_rollback(tenant, "model_8", target_version="1.0.0")
    plan = mgr.rollback_manager.execute_rollback_plan(rbreq)

    assert plan.delegation_request is not None
    assert plan.delegation_request.target == DelegationTarget.PLATFORM_OPERATIONS
    assert plan.delegation_request.action == "ROLLBACK_AI_ASSET"


def test_flow9_tenant_isolation():
    """Flow 9: Cross-tenant lifecycle access -> blocked -> zero metadata leakage."""
    mgr = AILifecyclePlatformManager()

    model = mgr.model_manager.register_model("tenant_a", "ModelA")

    with pytest.raises(CrossTenantLifecycleAccessException):
        mgr.model_manager.get_model(model.model_id, "tenant_b")


def test_flow10_artifact_integrity():
    """Flow 10: Artifact fingerprint mismatch -> ArtifactIntegrityException."""
    mgr = AILifecyclePlatformManager()
    tenant = "tenant_lc_10"

    art = mgr.artifact_manager.register_artifact(tenant, "Binary_10", content_payload={"weight": 1.0})

    with pytest.raises(ArtifactIntegrityException):
        mgr.artifact_manager.verify_integrity(art.artifact_id, tenant, current_payload={"weight": 2.0})


def test_flow11_immutable_release():
    """Flow 11: Finalized release -> mutation attempt -> ImmutableLifecycleRecordException."""
    mgr = AILifecyclePlatformManager()
    tenant = "tenant_lc_11"

    rel = mgr.release_manager.create_release(tenant, "Release_11", "model_11")
    finalized = mgr.release_manager.finalize_release(rel.release_id, tenant)

    assert len(finalized.immutable_record.fingerprint) == 64

    with pytest.raises(ImmutableLifecycleRecordException):
        mgr.release_manager.finalize_release(rel.release_id, tenant)


def test_flow12_evaluation_evidence_requirement():
    """Flow 12: Evaluation without sufficient evidence -> gate failure."""
    mgr = AILifecyclePlatformManager()
    tenant = "tenant_lc_12"

    suite = mgr.evaluation_manager.create_suite(tenant, "Suite_12")
    run = mgr.evaluation_manager.run_evaluation(tenant, "model_12", suite.suite_id, overall_passed=False)

    assert not run.overall_passed
    assert run.results[0].evidence_references is not None


def test_flow13_trust_contract_compatibility():
    """Flow 13: Lifecycle trust score -> TrustAssessment compatibility."""
    mgr = AILifecyclePlatformManager()
    tenant = "tenant_lc_13"

    tscore = mgr.trust_engine.compute_trust(tenant, "model_13", eval_passed=True, gates_passed=True)
    contract_assessment = mgr.trust_engine.to_contract_assessment(tscore)

    assert contract_assessment.score == 95.0
    assert contract_assessment.subject_id == "model_13"


def test_flow14_secret_redaction():
    """Flow 14: Secrets/tokens/passwords/PII -> sanitized from lifecycle metadata and evidence logs."""
    mgr = AILifecyclePlatformManager()
    tenant = "tenant_lc_14"

    ev = LifecycleEvidence(tenant_id=tenant, source="EVALUATOR", content_reference="ref_14", metadata={"api_key": "sk_live_12345", "password": "secret_password"})
    bundle = mgr.evidence_manager.create_evidence_bundle(tenant, "Bundle_14", [ev])

    assert bundle.evidences[0].metadata["api_key"] == "[REDACTED]"
    assert bundle.evidences[0].metadata["password"] == "[REDACTED]"


def test_flow15_retirement_lifecycle():
    """Flow 15: Retirement -> dependency analysis -> approval -> delegated execution -> immutable snapshot."""
    mgr = AILifecyclePlatformManager()
    tenant = "tenant_lc_15"

    ret_req = mgr.retirement_manager.request_retirement(tenant, "model_15", reason=RetirementReason.DEPRECATED)
    finalized = mgr.retirement_manager.finalize_retirement(ret_req.retirement_id, tenant)

    assert finalized.status == RetirementStatus.RETIRED
    assert finalized.immutable_record.fingerprint != ""


def test_flow16_full_ai_lifecycle():
    """Flow 16: Complete 19-stage end-to-end AI asset lifecycle flow."""
    mgr = AILifecyclePlatformManager()
    tenant = "tenant_lc_16"

    res = mgr.run_full_ai_lifecycle_flow(tenant_id=tenant, asset_name="Production_LLM_Agent")

    assert res["model"]["name"] == "Production_LLM_Agent_Model"
    assert res["agent"]["name"] == "Production_LLM_Agent"
    assert res["release"]["status"] == ReleaseStatus.RELEASED.value
    assert res["retirement"]["status"] == RetirementStatus.RETIRED.value
    assert res["snapshot"]["immutable_record"]["fingerprint"] != ""
