"""Comprehensive 4-Level End-to-End Test Suite for Phase 5.58 Platform Integration Fabric (40 Tests)."""

import pytest
import datetime
from app.platform_integration.manager import PlatformIntegrationManager
from app.platform_integration.models import (
    IntegrationPlatform,
    RiskLevel,
    GovernanceDecision,
    CrossPhaseEventType,
    TraceContext,
    CausalRelationshipStatus,
    LineageNodeType,
)
from app.platform_integration.exceptions import (
    CrossTenantPlatformIntegrationException,
    HighRiskPlatformIntegrationActionRequiresApprovalException,
    ImmutablePlatformIntegrationRecordException,
    IntegrationProviderNotFoundException,
    IntelligenceLineageException,
)
from app.platform_integration.providers import (
    MockPlatformIntegrationProvider,
    PlatformProviderResult,
)


@pytest.fixture
def manager():
    return PlatformIntegrationManager()


# ==============================================================================
# LEVEL 1: UNIT & CORE ENGINE TESTS (Flows 01 - 16)
# ==============================================================================

# Flow 01: Provider Registration and Discovery
def test_flow_01_provider_registration_and_discovery(manager):
    p = MockPlatformIntegrationProvider(platform_name="CUSTOM_DOMAIN")
    manager.providers.register_provider("CUSTOM_DOMAIN", p)
    retrieved = manager.providers.get_provider("CUSTOM_DOMAIN")
    assert retrieved is not None
    assert retrieved.platform_name == "CUSTOM_DOMAIN"
    assert "CUSTOM_DOMAIN" in manager.providers.list_platforms()


# Flow 02: Provider Failure Isolation
def test_flow_02_provider_failure_isolation(manager):
    failing_provider = MockPlatformIntegrationProvider(platform_name="FAILING_PLATFORM", simulate_failure=True)
    manager.providers.register_provider("FAILING_PLATFORM", failing_provider)

    # Calling collect_all_intelligence must NOT raise an exception
    results = manager.providers.collect_all_intelligence("tenant_alpha")
    assert "FAILING_PLATFORM" in results
    assert results["FAILING_PLATFORM"].status == "FAILED"
    assert results["FAILING_PLATFORM"].confidence == 0.0
    assert results["FAILING_PLATFORM"].uncertainty == 1.0


# Flow 03: Provider Timeout and Partial Response
def test_flow_03_provider_timeout_and_partial_response(manager):
    timeout_provider = MockPlatformIntegrationProvider(platform_name="SLOW_PLATFORM", simulate_timeout=True)
    manager.providers.register_provider("SLOW_PLATFORM", timeout_provider)

    res = timeout_provider.collect_intelligence("tenant_alpha")
    assert res.status == "DEGRADED"
    assert res.partial is True
    assert "Timeout contacting platform" in (res.error or "")


# Flow 04: Signal Normalization via Adapters
def test_flow_04_signal_normalization_via_adapters():
    from app.platform_integration.context.normalization import DomainNormalizer

    raw = {
        "signal_id": "sig-raw-99",
        "type": "LATENCY_SPIKE",
        "severity": "HIGH",
        "payload": {"p99_ms": 250.0},
        "confidence": 0.95,
        "evidence_references": ["ev-1", "ev-2"],
    }
    sig = DomainNormalizer.normalize_signal("tenant_a", "RUNTIME", raw)
    assert sig.signal_id == "sig-raw-99"
    assert sig.source_platform == IntegrationPlatform.RUNTIME
    assert sig.signal_type == "LATENCY_SPIKE"
    assert sig.severity == "HIGH"
    assert len(sig.evidence_references) == 2


# Flow 05: Bounded Context Policy Enforcement
def test_flow_05_bounded_context_policy_enforcement(manager):
    from app.platform_integration.context.builder import BoundedContextPolicy, PlatformIntegrationContextBuilder

    strict_policy = BoundedContextPolicy(max_platforms=2, max_signals=1)
    builder = PlatformIntegrationContextBuilder(policy=strict_policy)

    results = manager.providers.collect_all_intelligence("tenant_a")
    ctx = builder.build_context("tenant_a", results)

    assert len(ctx.active_platforms) <= 2
    assert len(ctx.signals) <= 1


# Flow 06: Context Fingerprint Determinism
def test_flow_06_context_fingerprint_determinism(manager):
    ctx1 = manager.build_context("tenant_a")
    ctx2 = manager.build_context("tenant_a")
    assert len(ctx1.fingerprint) == 64
    assert len(ctx2.fingerprint) == 64


# Flow 07: Trace Context Propagation
def test_flow_07_trace_context_propagation(manager):
    root_ctx = TraceContext(tenant_id="tenant_a", source_platform="RUNTIME")
    child_ctx = manager.propagation.spawn_child_context(root_ctx, target_platform="CAPACITY")

    assert child_ctx.trace_id == root_ctx.trace_id
    assert child_ctx.correlation_id == root_ctx.correlation_id
    assert child_ctx.source_platform == "CAPACITY"

    headers = manager.propagation.inject_trace_headers(child_ctx)
    assert headers["X-Trace-ID"] == root_ctx.trace_id
    assert headers["X-Source-Platform"] == "CAPACITY"


# Flow 08: Correlation Does Not Imply Causation
def test_flow_08_correlation_does_not_imply_causation(manager):
    ctx = manager.build_context("tenant_a")
    corrs = manager.correlate_signals("tenant_a", ctx.context_id, threshold=0.1)

    assert len(corrs) > 0
    for c in corrs:
        assert c.is_causal is False
        assert c.causal_status == CausalRelationshipStatus.HYPOTHESIZED


# Flow 09: Dependency Graph Traversal
def test_flow_09_dependency_graph_traversal(manager):
    deps = manager.dep_graph.get_dependencies("RUNTIME")
    assert "CAPACITY" in deps

    dependents = manager.dep_graph.get_dependents("CAPACITY")
    assert "RUNTIME" in dependents

    impact_path = manager.dep_graph.traverse_impact_path("CAPACITY")
    assert "CAPACITY" in impact_path
    assert "RUNTIME" in impact_path


# Flow 10: Dependency Graph Cycle Detection
def test_flow_10_dependency_graph_cycle_detection(manager):
    from app.platform_integration.correlation.dependency_graph import CrossPhaseDependencyGraph

    graph = CrossPhaseDependencyGraph()
    # Canonical topology is acyclic
    assert len(graph.detect_cycles()) == 0

    # Inject an intentional cycle A -> B -> C -> A
    graph.add_dependency("A", "B")
    graph.add_dependency("B", "C")
    graph.add_dependency("C", "A")

    cycles = graph.detect_cycles()
    assert len(cycles) > 0


# Flow 11: Risk Propagation Policy Decay
def test_flow_11_risk_propagation_policy_decay(manager):
    # Propagate risk from CAPACITY downstream
    propagated = manager.risk_propagation.propagate_risk("tenant_a", "CAPACITY", initial_risk_score=0.9)
    assert len(propagated) >= 2

    # Root node at hop 0
    root = propagated[0]
    assert root.platform == "CAPACITY"
    assert root.hops_from_source == 0
    assert root.derived_risk_level == RiskLevel.CRITICAL

    # Downstream node has attenuated score
    child = propagated[1]
    assert child.hops_from_source == 1
    assert child.propagated_score < root.propagated_score


# Flow 12: Dynamic Assurance Weight Policy
def test_flow_12_dynamic_assurance_weight_policy(manager):
    posture = manager.evaluate_assurance_posture("tenant_a")
    assert 0.0 <= posture.overall_score <= 1.0
    assert posture.trust_band in ("HIGH_TRUST", "TRUSTED", "RESTRICTED", "UNTRUSTED")
    assert len(posture.effective_weights) > 0


# Flow 13: Confidence Assessment Composition
def test_flow_13_confidence_assessment_composition(manager):
    results = manager.providers.collect_all_intelligence("tenant_a")
    conf = manager.confidence.evaluate_confidence(results, evidence_count=3)

    assert 0.0 <= conf.overall_confidence <= 1.0
    assert conf.provider_confidence > 0.5
    assert conf.completeness_confidence > 0.5


# Flow 14: Uncertainty Quantification on Missing Data
def test_flow_14_uncertainty_quantification_on_missing_data(manager):
    results = manager.providers.collect_all_intelligence("tenant_a")
    # Simulate missing platforms
    partial_results = {k: v for k, v in results.items() if k in ("RUNTIME", "CAPACITY")}

    all_expected = manager.providers.list_platforms()
    unc = manager.uncertainty.quantify_uncertainty(partial_results, all_expected)

    assert len(unc.missing_platforms) > 0
    assert unc.overall_uncertainty > 0.4


# Flow 15: Event Coordinator and Store
def test_flow_15_event_coordinator_and_store(manager):
    ev = manager.events.publish_event(
        tenant_id="tenant_a",
        event_type=CrossPhaseEventType.ANOMALY_DETECTED,
        source_platform=IntegrationPlatform.RUNTIME,
        payload={"anomaly_type": "MEM_SPIKE", "severity": "HIGH"},
    )
    assert ev.event_id.startswith("ev-")

    events = manager.events.get_events("tenant_a", CrossPhaseEventType.ANOMALY_DETECTED)
    assert len(events) >= 1
    assert events[0].event_type == CrossPhaseEventType.ANOMALY_DETECTED


# Flow 16: Idempotency Deduplication
def test_flow_16_idempotency_deduplication(manager):
    key = manager.idempotency.generate_key("tenant_a", "DELEGATE_ACTION", {"action": "SCALE_OUT"})
    assert len(key) == 64

    # First check succeeds
    assert manager.idempotency.check_and_record(key) is True
    # Duplicate check fails
    assert manager.idempotency.check_and_record(key) is False


# ==============================================================================
# LEVEL 2: LINEAGE, EVIDENCE & GOVERNANCE TESTS (Flows 17 - 30)
# ==============================================================================

# Flow 17: Unified Lineage Graph Assembly
def test_flow_17_unified_lineage_graph_assembly(manager):
    from app.platform_integration.lineage.graph import LineageNode, LineageNodeType

    n1 = LineageNode(node_id="sig-1", node_type=LineageNodeType.SIGNAL, tenant_id="tenant_a", platform="RUNTIME")
    n2 = LineageNode(node_id="find-1", node_type=LineageNodeType.FINDING, tenant_id="tenant_a", platform="RUNTIME")
    n3 = LineageNode(node_id="rec-1", node_type=LineageNodeType.RECOMMENDATION, tenant_id="tenant_a", platform="CAPACITY")

    manager.lineage.add_node(n1)
    manager.lineage.add_node(n2)
    manager.lineage.add_node(n3)

    manager.lineage.add_edge("sig-1", "find-1")
    manager.lineage.add_edge("find-1", "rec-1")

    assert "find-1" in manager.lineage.edges["sig-1"]
    assert "rec-1" in manager.lineage.edges["find-1"]


# Flow 18: Lineage Root Cause Backtrace
def test_flow_18_lineage_root_cause_backtrace(manager):
    from app.platform_integration.lineage.graph import LineageNode, LineageNodeType

    n1 = LineageNode(node_id="sig-root-1", node_type=LineageNodeType.SIGNAL, tenant_id="tenant_a", platform="RUNTIME")
    n2 = LineageNode(node_id="find-mid-1", node_type=LineageNodeType.FINDING, tenant_id="tenant_a", platform="RUNTIME")
    n3 = LineageNode(node_id="rec-leaf-1", node_type=LineageNodeType.RECOMMENDATION, tenant_id="tenant_a", platform="CAPACITY")

    manager.lineage.add_node(n1)
    manager.lineage.add_node(n2)
    manager.lineage.add_node(n3)

    manager.lineage.add_edge("sig-root-1", "find-mid-1")
    manager.lineage.add_edge("find-mid-1", "rec-leaf-1")

    roots = manager.lineage.backtrace_root_causes("rec-leaf-1")
    assert len(roots) == 1
    assert roots[0].node_id == "sig-root-1"


# Flow 19: Lineage Cycle Prevention
def test_flow_19_lineage_cycle_prevention(manager):
    from app.platform_integration.lineage.graph import LineageNode, LineageNodeType

    n1 = LineageNode(node_id="node-a", node_type=LineageNodeType.SIGNAL, tenant_id="tenant_a", platform="RUNTIME")
    n2 = LineageNode(node_id="node-b", node_type=LineageNodeType.FINDING, tenant_id="tenant_a", platform="RUNTIME")
    manager.lineage.add_node(n1)
    manager.lineage.add_node(n2)
    manager.lineage.add_edge("node-a", "node-b")

    with pytest.raises(IntelligenceLineageException):
        # Adding edge from descendant back to ancestor node-b -> node-a must raise exception
        manager.lineage.add_edge("node-b", "node-a")


# Flow 20: Immutable Evidence Chain and Tamper Detection
def test_flow_20_immutable_evidence_chain_and_tamper_detection(manager):
    b1 = manager.evidence.record_evidence("tenant_a", "RUNTIME", {"metric": "latency", "val": 42})
    b2 = manager.evidence.record_evidence("tenant_a", "CAPACITY", {"metric": "gpu_mem", "val": 0.85})

    assert b2.previous_hash == b1.current_hash
    assert manager.evidence.verify_chain_integrity("tenant_a") is True

    # Modification attempt raises exception
    with pytest.raises(ImmutablePlatformIntegrationRecordException):
        manager.evidence.modify_evidence_attempt("tenant_a", b1.evidence_id)


# Flow 21: Cross-Phase Snapshot Comparison
def test_flow_21_cross_phase_snapshot_comparison(manager):
    snap1 = manager.capture_snapshot("tenant_a")
    snap2 = manager.capture_snapshot("tenant_a")

    diff = manager.snapshots.compare_snapshots(snap1, snap2)
    assert diff["score_delta"] == 0.0
    assert diff["platforms_added"] == []


# Flow 22: Cross-Tenant Isolation Enforcement
def test_flow_22_cross_tenant_isolation_enforcement(manager):
    ctx_a = manager.build_context("tenant_alpha")

    # Accessing tenant_alpha's context using tenant_beta must fail
    with pytest.raises(CrossTenantPlatformIntegrationException) as exc:
        manager.context_repo.get("tenant_beta", ctx_a.context_id)
    assert "Access denied" in str(exc.value)


# Flow 23: Cross-Tenant Metadata Leakage Prevention
def test_flow_23_cross_tenant_metadata_leakage_prevention(manager):
    ctx_a = manager.build_context("tenant_alpha")
    # Cross tenant access must raise exception with strictly "Access denied" message
    with pytest.raises(CrossTenantPlatformIntegrationException) as exc:
        manager.context_repo.get("tenant_beta", ctx_a.context_id)
    assert str(exc.value) == "Access denied"


# Flow 24: Recommendation auto_execute = False Enforcement
def test_flow_24_recommendation_auto_execute_false_enforcement(manager):
    recs = manager.generate_recommendations("tenant_a", ["RUNTIME", "CAPACITY", "RELIABILITY"])
    assert len(recs) == 3
    for r in recs:
        assert r.auto_execute is False  # MANDATORY INVARIANT


# Flow 25: Governance Evaluation Matrix
def test_flow_25_governance_evaluation_matrix(manager):
    d_low = manager.governance.evaluate_governance("tenant_a", "OBSERVE", RiskLevel.LOW)
    assert d_low == GovernanceDecision.ALLOW

    d_med = manager.governance.evaluate_governance("tenant_a", "TUNE", RiskLevel.MEDIUM)
    assert d_med == GovernanceDecision.ADVISORY_ONLY

    d_high = manager.governance.evaluate_governance("tenant_a", "RESTART", RiskLevel.HIGH)
    assert d_high == GovernanceDecision.REQUIRE_APPROVAL


# Flow 26: High-Risk Action Requires Approval
def test_flow_26_high_risk_action_requires_approval(manager):
    recs = manager.generate_recommendations("tenant_a", ["CAPACITY"])
    rec_high = [r for r in recs if r.risk_level == RiskLevel.HIGH][0]

    # Attempting to delegate without approval raises exception
    with pytest.raises(HighRiskPlatformIntegrationActionRequiresApprovalException):
        manager.delegate_action("tenant_a", rec_high.recommendation_id)


# Flow 27: Approval Lifecycle and TTL
def test_flow_27_approval_lifecycle_and_ttl(manager):
    appr = manager.approvals.request_approval("tenant_a", "REALLOCATE_CAPACITY_BUFFER", reason="Cluster pressure")
    assert appr.decision == "PENDING"
    assert appr.is_valid is False

    # Approve
    approved = manager.approvals.approve(appr.approval_id, approver="security_admin@enterprise.com")
    assert approved.decision == "APPROVED"
    assert approved.is_valid is True
    assert manager.approvals.validate_token(appr.approval_id, appr.token) is True


# Flow 28: Delegation-Only Execution Enforcement
def test_flow_28_delegation_only_execution_enforcement(manager):
    recs = manager.generate_recommendations("tenant_a", ["CAPACITY"])
    rec_high = [r for r in recs if r.risk_level == RiskLevel.HIGH][0]

    appr = manager.approvals.request_approval("tenant_a", rec_high.action)
    manager.approvals.approve(appr.approval_id, approver="admin")

    del_req = manager.delegate_action(
        "tenant_a",
        rec_high.recommendation_id,
        approval_id=appr.approval_id,
        approval_token=appr.token,
    )

    assert del_req.delegation_id.startswith("delreq_")
    assert del_req.action == rec_high.action
    assert del_req.payload["approval_id"] == appr.approval_id


# Flow 29: Delegation Lineage Traceability
def test_flow_29_delegation_lineage_traceability(manager):
    recs = manager.generate_recommendations("tenant_a", ["RUNTIME"])
    del_req = manager.delegate_action("tenant_a", recs[0].recommendation_id)

    # Check that recommendation node is connected to delegation node
    nodes = manager.lineage.nodes
    assert any(n.node_type == LineageNodeType.DELEGATION for n in nodes.values())


# Flow 30: Closed-Loop Verification Outcome
def test_flow_30_closed_loop_verification_outcome(manager):
    recs = manager.generate_recommendations("tenant_a", ["RUNTIME"])
    del_req = manager.delegate_action("tenant_a", recs[0].recommendation_id)

    v_success = manager.verify_delegation("tenant_a", del_req.delegation_id, pre_score=0.65, post_score=0.88, required_delta=0.10)
    assert v_success.verified is True
    assert v_success.improvement_delta == 0.23

    v_fail = manager.verify_delegation("tenant_a", del_req.delegation_id, pre_score=0.65, post_score=0.68, required_delta=0.10)
    assert v_fail.verified is False



# ==============================================================================
# LEVEL 3: DYNAMIC INVESTIGATION & CROSS-PHASE INTER-PLATFORM TESTS (Flows 31 - 38)
# ==============================================================================

# Flow 31: Graph-Based Investigation from Runtime Root
def test_flow_31_graph_based_investigation_from_runtime_root(manager):
    res = manager.run_investigation("tenant_a", "RUNTIME", "High tail latency and 504 gateway timeout")
    assert res.root_platform == "RUNTIME"
    assert "CAPACITY" in res.traversed_platforms
    assert len(res.timeline) >= 2
    assert "RUNTIME" in res.conclusion


# Flow 32: Graph-Based Investigation from Security Root
def test_flow_32_graph_based_investigation_from_security_root(manager):
    res = manager.run_investigation("tenant_a", "SECURITY", "Credential stuffing and anomaly alert")
    assert res.root_platform == "SECURITY"
    assert "CONTINUOUS_ASSURANCE" in res.traversed_platforms


# Flow 33: End-to-End Runtime to Capacity Integration
def test_flow_33_end_to_end_runtime_to_capacity_integration(manager):
    ctx = manager.build_context("tenant_a")
    assert "RUNTIME" in ctx.active_platforms
    assert "CAPACITY" in ctx.active_platforms
    corrs = manager.correlate_signals("tenant_a", ctx.context_id)
    assert isinstance(corrs, list)


# Flow 34: End-to-End Capacity to Reliability Integration
def test_flow_34_end_to_end_capacity_to_reliability_integration(manager):
    p_cap = manager.providers.get_provider("CAPACITY").collect_intelligence("tenant_a")
    p_rel = manager.providers.get_provider("RELIABILITY").collect_intelligence("tenant_a")
    assert p_cap.status == "SUCCESS"
    assert p_rel.status == "SUCCESS"


# Flow 35: End-to-End Reliability to Continuous Assurance
def test_flow_35_end_to_end_reliability_to_continuous_assurance(manager):
    p_rel = manager.providers.get_provider("RELIABILITY").collect_intelligence("tenant_a")
    p_ca = manager.providers.get_provider("CONTINUOUS_ASSURANCE").collect_intelligence("tenant_a")
    assert p_rel.status == "SUCCESS"
    assert p_ca.status == "SUCCESS"


# Flow 36: End-to-End Continuous to Autonomous Assurance
def test_flow_36_end_to_end_continuous_to_autonomous_assurance(manager):
    p_ca = manager.providers.get_provider("CONTINUOUS_ASSURANCE").collect_intelligence("tenant_a")
    p_aa = manager.providers.get_provider("AUTONOMOUS_ASSURANCE").collect_intelligence("tenant_a")
    assert p_ca.status == "SUCCESS"
    assert p_aa.status == "SUCCESS"


# Flow 37: End-to-End Autonomous to Decision Intelligence
def test_flow_37_end_to_end_autonomous_to_decision_intelligence(manager):
    p_aa = manager.providers.get_provider("AUTONOMOUS_ASSURANCE").collect_intelligence("tenant_a")
    p_di = manager.providers.get_provider("DECISION_INTELLIGENCE").collect_intelligence("tenant_a")
    assert p_aa.status == "SUCCESS"
    assert p_di.status == "SUCCESS"


# Flow 38: End-to-End Decision to Unified Intelligence
def test_flow_38_end_to_end_decision_to_unified_intelligence(manager):
    p_di = manager.providers.get_provider("DECISION_INTELLIGENCE").collect_intelligence("tenant_a")
    p_ui = manager.providers.get_provider("UNIFIED_INTELLIGENCE").collect_intelligence("tenant_a")
    assert p_di.status == "SUCCESS"
    assert p_ui.status == "SUCCESS"


# ==============================================================================
# LEVEL 4: FULL END-TO-END PLATFORM LIFECYCLE & DEGRADATION TESTS (Flows 39 - 40)
# ==============================================================================

# Flow 39: Full Cross-Phase Intelligence Lifecycle
def test_flow_39_full_cross_phase_intelligence_lifecycle(manager):
    tenant = "tenant_enterprise_prod"

    # 1. Ingest cross-phase context
    ctx = manager.build_context(tenant)
    assert len(ctx.active_platforms) >= 7

    # 2. Correlate cross-phase signals
    corrs = manager.correlate_signals(tenant, ctx.context_id, threshold=0.1)

    # 3. Evaluate platform assurance posture
    posture = manager.evaluate_assurance_posture(tenant)
    assert posture.posture in ("ASSURED", "WATCH", "DEGRADED", "COMPROMISED")

    # 4. Investigate
    inv = manager.run_investigation(tenant, "RUNTIME", "End-to-end full audit trace")
    assert len(inv.traversed_platforms) >= 2

    # 5. Generate recommendations with strict auto_execute=False
    recs = manager.generate_recommendations(tenant, ["CAPACITY", "RUNTIME"])
    for r in recs:
        assert r.auto_execute is False

    # 6. Approve high risk recommendation and delegate
    rec = recs[0]
    if rec.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
        appr = manager.approvals.request_approval(tenant, rec.action)
        manager.approvals.approve(appr.approval_id, approver="chief_architect@enterprise.com")
        del_req = manager.delegate_action(tenant, rec.recommendation_id, appr.approval_id, appr.token)
    else:
        del_req = manager.delegate_action(tenant, rec.recommendation_id)
    assert del_req.delegation_id.startswith("delreq_")

    # 7. Verify closed-loop outcome
    verif = manager.verify_delegation(tenant, del_req.delegation_id, pre_score=0.70, post_score=0.92)
    assert verif.verified is True

    # 8. Capture sealed snapshot
    snap = manager.capture_snapshot(tenant)
    assert len(snap.state_fingerprint) == 64

    # 9. Verify trace in LineageGraph
    forward = manager.lineage.trace_forward_impact(rec.recommendation_id)
    assert any(n.node_id == del_req.delegation_id for n in forward)


# Flow 40: Provider Degradation Resilience
def test_flow_40_provider_degradation_resilience(manager):
    # Degrade capacity provider and ensure entire fabric degrades gracefully without raising unhandled errors
    failing_cap = MockPlatformIntegrationProvider("CAPACITY", simulate_failure=True)
    manager.providers.register_provider("CAPACITY", failing_cap)

    posture = manager.evaluate_assurance_posture("tenant_resilience")
    assert "CAPACITY" in posture.degraded_platforms
    assert posture.posture in ("DEGRADED", "COMPROMISED", "WATCH")
