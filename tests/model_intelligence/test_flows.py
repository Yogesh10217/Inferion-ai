"""Mandatory 20 E2E Integration Flow Tests for Model Intelligence Platform (Phase 5.44)."""

import pytest

from app.model_intelligence import (
    BenchmarkResult,
    CrossTenantModelIntelligenceException,
    DriftSeverity,
    EvaluationMetric,
    EvaluationType,
    HallucinationSeverity,
    HallucinationType,
    ModelDriftType,
    ModelEvidence,
    ModelGovernanceDecisionStatus,
    ModelIncidentSeverity,
    ModelIncidentStatus,
    ModelIntelligenceManager,
    ModelProviderReference,
    ModelRemediationAction,
    ModelRemediationPriority,
    ModelSecurityRisk,
    ModelSignalSource,
    ModelSignalType,
    ModelTrustDimension,
    ModelTrustFactor,
    ModelType,
    QualityDimension,
    QualityScore,
    ReliabilityDimension,
    ReliabilityScore,
    SafetyRisk,
)


@pytest.fixture
def manager():
    return ModelIntelligenceManager()


def test_flow_01_model_registration_and_tenant_isolation(manager):
    """Flow 1: Model Registration & Tenant Isolation."""
    prov = ModelProviderReference(provider_id="p-1", provider_name="OpenAI")
    m1 = manager.registry.register_model(name="GPT-4o", tenant_id="tenant-a", model_type=ModelType.LLM, provider=prov)
    assert m1.name == "GPT-4o"
    assert m1.tenant_id == "tenant-a"

    fetched = manager.registry.get_model(m1.model_id, "tenant-a")
    assert fetched.model_id == m1.model_id


def test_flow_02_cross_tenant_model_access_blocked(manager):
    """Flow 2: Cross-Tenant Model Access Blocked (ZERO metadata leakage)."""
    prov = ModelProviderReference(provider_id="p-1", provider_name="Anthropic")
    m1 = manager.registry.register_model(
        name="Claude-3-5-Sonnet", tenant_id="tenant-alpha", model_type=ModelType.LLM, provider=prov
    )

    with pytest.raises(CrossTenantModelIntelligenceException) as exc_info:
        manager.registry.get_model(m1.model_id, "tenant-beta")

    # Verify zero metadata leakage
    err_msg = str(exc_info.value)
    assert m1.model_id not in err_msg
    assert "Claude-3-5-Sonnet" not in err_msg
    assert "tenant-alpha" not in err_msg


def test_flow_03_model_version_comparison(manager):
    """Flow 3: Model Version Comparison."""
    prov = ModelProviderReference(provider_id="p-1", provider_name="Internal")
    m1 = manager.registry.register_model(
        name="InternalLLM", tenant_id="tenant-1", model_type=ModelType.LLM, provider=prov
    )

    assessment = manager.version_manager.compare_versions(
        model_id=m1.model_id,
        base_version_tag="1.0.0",
        target_version_tag="1.1.0",
        tenant_id="tenant-1",
        latency_delta_ms=10.0,
        accuracy_delta=0.05,
    )
    assert assessment.comparison.recommendation == "PROCEED"
    assert assessment.risk_level == "LOW"


def test_flow_04_model_evaluation(manager):
    """Flow 4: Model Evaluation."""
    metrics = [
        EvaluationMetric(name="accuracy", score=0.92, passed=True),
        EvaluationMetric(name="latency", score=0.88, passed=True),
    ]
    ev = manager.evaluation_manager.create_evaluation(
        model_id="mod-1",
        tenant_id="tenant-1",
        version_tag="1.0.0",
        eval_type=EvaluationType.DETERMINISTIC,
        metrics=metrics,
    )
    assert ev.result.overall_score == pytest.approx(0.90)
    assert ev.result.passed is True
    assert ev.evidence.fingerprint is not None


def test_flow_05_model_benchmark_comparison(manager):
    """Flow 5: Model Benchmark Comparison."""
    res1 = BenchmarkResult(
        model_id="m-1", model_name="Model A", version_tag="1.0.0", suite_name="Reasoning", score=85.0
    )
    res2 = BenchmarkResult(
        model_id="m-2", model_name="Model B", version_tag="1.0.0", suite_name="Reasoning", score=92.0
    )

    manager.benchmark_manager.run_benchmark(tenant_id="tenant-1", suite_name="Reasoning", results=[res1, res2])
    comp = manager.benchmark_manager.compare_models(
        tenant_id="tenant-1",
        suite_name="Reasoning",
        baseline_model_id="m-1",
        candidate_model_id="m-2",
        baseline_score=85.0,
        candidate_score=92.0,
    )
    assert comp.winner == "m-2"
    assert comp.diff_score == 7.0


def test_flow_06_performance_degradation_detection(manager):
    """Flow 6: Performance Degradation Detection."""
    perf = manager.performance_manager.record_performance(
        model_id="m-1",
        tenant_id="tenant-1",
        latency_p95_ms=650.0,  # Degradation > 500ms
        error_rate_percentage=0.5,
    )
    assert perf.assessment.degraded is True
    assert perf.assessment.trend.value == "DEGRADING"


def test_flow_07_output_quality_assessment(manager):
    """Flow 7: Output Quality Assessment."""
    scores = [
        QualityScore(dimension=QualityDimension.CORRECTNESS, score=0.95),
        QualityScore(dimension=QualityDimension.RELEVANCE, score=0.90),
    ]
    qa = manager.quality_manager.evaluate_quality(model_id="m-1", tenant_id="tenant-1", scores=scores)
    assert qa.overall_quality_score == pytest.approx(0.925)
    assert qa.status.value == "EXCELLENT"


def test_flow_08_hallucination_detection(manager):
    """Flow 8: Hallucination Detection."""
    finding = manager.hallucination_manager.create_finding(
        hallucination_type=HallucinationType.UNSUPPORTED_CLAIMS,
        severity=HallucinationSeverity.HIGH,
        confidence=0.89,
        description="Model claimed unverified statistic.",
    )
    assess = manager.hallucination_manager.analyze_hallucinations(
        model_id="m-1",
        tenant_id="tenant-1",
        total_evaluated=100,
        findings=[finding],
    )
    assert assess.hallucination_rate == 0.01
    assert len(assess.findings) == 1


def test_flow_09_model_drift_detection(manager):
    """Flow 9: Model Drift Detection."""
    drift = manager.drift_manager.detect_drift(
        model_id="m-1",
        tenant_id="tenant-1",
        drift_type=ModelDriftType.BEHAVIORAL_DRIFT,
        drift_score=0.55,  # SEVERE
    )
    assert drift.severity == DriftSeverity.SEVERE
    assess = manager.drift_manager.assess_model_drift("m-1", "tenant-1")
    assert assess.requires_remediation is True


def test_flow_10_reliability_failure_detection(manager):
    """Flow 10: Reliability Failure Detection."""
    scores = [ReliabilityScore(dimension=ReliabilityDimension.AVAILABILITY, score=0.98)]
    rel = manager.reliability_manager.assess_reliability(model_id="m-1", tenant_id="tenant-1", scores=scores)
    assert rel.resilient is True


def test_flow_11_safety_risk_detection(manager):
    """Flow 11: Safety Risk Detection."""
    finding = manager.safety_manager.create_finding(
        safety_risk=SafetyRisk.TOXICITY,
        severity="HIGH",
        description="Potential toxic language in edge case prompt.",
    )
    safety = manager.safety_manager.evaluate_safety(model_id="m-1", tenant_id="tenant-1", findings=[finding])
    assert safety.safety_score < 1.0


def test_flow_12_security_risk_detection(manager):
    """Flow 12: Security Risk Detection."""
    finding = manager.security_manager.create_finding(
        security_risk=ModelSecurityRisk.PROMPT_INJECTION_EXPOSURE,
        severity="HIGH",
        description="Prompt injection vulnerability detected.",
    )
    security = manager.security_manager.assess_security(model_id="m-1", tenant_id="tenant-1", findings=[finding])
    assert security.is_secure is False


def test_flow_13_model_incident_creation(manager):
    """Flow 13: Model Incident Creation."""
    inc = manager.incident_manager.create_incident(
        model_id="m-1",
        tenant_id="tenant-1",
        title="High Latency Spike",
        severity=ModelIncidentSeverity.HIGH,
    )
    assert inc.status == ModelIncidentStatus.DETECTED
    updated = manager.incident_manager.update_status(inc.incident_id, "tenant-1", ModelIncidentStatus.INVESTIGATING)
    assert updated.status == ModelIncidentStatus.INVESTIGATING


def test_flow_14_high_risk_model_remediation_requires_approval(manager):
    """Flow 14: High-Risk Model Remediation Requires Approval."""
    dec = manager.governance_engine.evaluate_action(
        action_type="production_model_rollback",
        model_id="m-1",
        tenant_id="tenant-1",
    )
    assert dec.status == ModelGovernanceDecisionStatus.REQUIRE_APPROVAL


def test_flow_15_delegation_only_enforcement(manager):
    """Flow 15: Delegation-Only Enforcement (No direct model mutation)."""
    act = ModelRemediationAction(action_id="act-1", action_name="rollback_recommendation", target_resource_id="m-1")
    plan = manager.remediation_manager.create_plan(
        model_id="m-1", tenant_id="tenant-1", priority=ModelRemediationPriority.HIGH, actions=[act]
    )
    exec_plan = manager.remediation_manager.execute_plan_via_delegation(plan.plan_id, "tenant-1")

    assert len(exec_plan.delegation_requests) == 1
    assert exec_plan.delegation_requests[0].action == "rollback_recommendation"


def test_flow_16_sensitive_data_redaction(manager):
    """Flow 16: Sensitive Data Redaction."""
    source = ModelSignalSource(source_id="src-1", source_name="data_intelligence")
    raw_payload = {
        "api_key": "secret_key_12345",
        "model_id": "m-1",
        "user_token": "bearer_abc",
    }
    sig = manager.signal_manager.ingest_signal(
        model_id="m-1",
        tenant_id="tenant-1",
        signal_type=ModelSignalType.PERFORMANCE_SIGNAL,
        source=source,
        raw_payload=raw_payload,
    )
    assert sig.payload.get("api_key") != "secret_key_12345"
    assert sig.payload.get("user_token") != "bearer_abc"


def test_flow_17_immutable_evidence(manager):
    """Flow 17: Immutable Evidence (SHA-256 integrity)."""
    ev = ModelEvidence(evidence_id="ev-1", evidence_type="EVAL", reference_id="r-1", data_ref="ref://data")
    bundle = manager.evidence_manager.create_evidence_bundle(model_id="m-1", tenant_id="tenant-1", evidences=[ev])
    assert bundle.finalized is True
    assert bundle.integrity.fingerprint is not None


def test_flow_18_model_trust_assessment(manager):
    """Flow 18: Model Trust Assessment."""
    factors = [ModelTrustFactor(dimension=ModelTrustDimension.QUALITY, score=95.0, weight=1.0)]
    trust = manager.trust_engine.calculate_trust(model_id="m-1", tenant_id="tenant-1", factors=factors)
    assert trust.trust_score.overall_score == 95.0
    assert trust.platform_trust_assessment.band.value in ["HIGH_TRUST", "TRUSTED"]


def test_flow_19_learning_does_not_auto_execute(manager):
    """Flow 19: Learning Does Not Auto Execute (auto_execute == False)."""
    rec = manager.learning_manager.generate_recommendation(
        target_model_id="m-1",
        tenant_id="tenant-1",
        pattern_name="HighLatencyPattern",
        recommendation_text="Consider optimizing prompt template.",
        reasoning="P95 latency exceeded baseline.",
    )
    assert rec.recommendation.auto_execute is False


def test_flow_20_full_enterprise_model_intelligence_lifecycle(manager):
    """Flow 20: Full Enterprise Model Intelligence Lifecycle (30 steps)."""
    res = manager.run_full_lifecycle(
        model_name="EnterpriseModelV1",
        tenant_id="enterprise-tenant",
        model_type=ModelType.LLM,
        provider_name="EnterpriseProvider",
    )
    assert res["status"] == "SUCCESS"
    assert res["learning_auto_execute"] is False
    assert res["cost_tracked_usd"] > 0.0
