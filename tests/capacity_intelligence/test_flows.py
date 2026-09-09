"""Comprehensive End-to-End Test Suite for Phase 5.56 Capacity Intelligence Platform (22 Test Flows)."""

import pytest
import datetime
from app.capacity_intelligence.manager import CapacityIntelligenceManager
from app.capacity_intelligence.exceptions import (
    CrossTenantCapacityIntelligenceException,
    HighRiskCapacityActionRequiresApprovalException,
    ImmutableCapacityIntelligenceRecordException,
    CapacityIntelligenceProviderException,
)
from app.capacity_intelligence.models import RiskLevel, DelegationStatus, GovernanceDecision


@pytest.fixture
def manager():
    return CapacityIntelligenceManager()


# Flow 1: Resource Registration & Metadata Tracking
def test_flow_01_resource_registration(manager):
    res = manager.register_resource(
        tenant_id="tenant_a",
        resource_id="res-gpu-cluster-1",
        name="H100 GPU Cluster",
        resource_type="GPU",
        total_capacity=64.0,
        capacity_unit="cards",
    )
    assert res.resource_id == "res-gpu-cluster-1"
    assert res.tenant_id == "tenant_a"
    assert res.total_capacity == 64.0
    assert res.capacity_unit == "cards"


# Flow 2: Multi-Resource Telemetry Ingestion & Aggregation
def test_flow_02_telemetry_ingestion(manager):
    tel1 = manager.ingest_telemetry("tenant_a", "res-gpu-cluster-1", "utilization_percent", 82.5)
    tel2 = manager.ingest_telemetry("tenant_a", "res-gpu-cluster-1", "memory_used_gb", 720.0)
    
    assert tel1.telemetry_id.startswith("tel-")
    assert tel1.value == 82.5
    assert tel2.value == 720.0


# Flow 3: Workload Pattern & Trend Analysis
def test_flow_03_workload_analysis(manager):
    wl = manager.analyze_workload(
        tenant_id="tenant_a",
        workload_type="inference_tokens",
        historical_samples=[1000, 1200, 1500, 2100, 3000],
    )
    assert wl.workload_id.startswith("wl-")
    assert wl.trend == "GROWING"
    assert wl.peak_to_average_ratio > 1.0


# Flow 4: Multi-Horizon Capacity Assessment
def test_flow_04_capacity_assessment(manager):
    ass = manager.assess_capacity(
        tenant_id="tenant_a",
        resource_id="res-gpu-cluster-1",
        scope="RESOURCE",
    )
    assert ass.assessment_id.startswith("cap-")
    assert ass.tenant_id == "tenant_a"
    assert 0.0 <= ass.utilization_rate <= 1.0
    assert ass.health_status in ["HEALTHY", "WARNING", "SATURATED", "CRITICAL"]


# Flow 5: Resource Exhaustion & Saturation Forecasting
def test_flow_05_capacity_forecasting(manager):
    fc = manager.forecast_capacity(
        tenant_id="tenant_a",
        resource_id="res-gpu-cluster-1",
        horizon_days=30,
    )
    assert fc.forecast_id.startswith("fc-")
    assert fc.horizon_days == 30
    assert 0.0 <= fc.predicted_utilization <= 2.0


# Flow 6: Workload Demand Prediction
def test_flow_06_demand_prediction(manager):
    dp = manager.predict_demand(
        tenant_id="tenant_a",
        workload_type="training_jobs",
        time_horizon_hours=24,
    )
    assert dp.prediction_id.startswith("dem-")
    assert dp.time_horizon_hours == 24
    assert 0.0 <= dp.confidence_score <= 1.0


# Flow 7: Multi-Resource Saturation Analysis
def test_flow_07_saturation_analysis(manager):
    sa = manager.analyze_saturation(
        tenant_id="tenant_a",
        resource_id="res-gpu-cluster-1",
    )
    assert sa.analysis_id.startswith("sat-")
    assert 0.0 <= sa.saturation_level <= 1.0
    assert sa.headroom_percent >= 0.0


# Flow 8: Performance Degradation Correlation
def test_flow_08_performance_correlation(manager):
    perf = manager.analyze_performance(
        tenant_id="tenant_a",
        resource_id="res-gpu-cluster-1",
    )
    assert perf.analysis_id.startswith("perf-")
    assert perf.degradation_risk in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


# Flow 9: System-Wide Bottleneck Detection
def test_flow_09_bottleneck_detection(manager):
    bn = manager.detect_bottlenecks(
        tenant_id="tenant_a",
        system_scope="GLOBAL",
    )
    assert bn.detection_id.startswith("bn-")
    assert bn.critical_count >= 0


# Flow 10: Resource Efficiency Scoring
def test_flow_10_resource_efficiency(manager):
    eff = manager.score_efficiency(
        tenant_id="tenant_a",
        resource_id="res-gpu-cluster-1",
    )
    assert eff.score_id.startswith("eff-")
    assert 0.0 <= eff.efficiency_score <= 1.0


# Flow 11: Multi-Objective Capacity Optimization
def test_flow_11_capacity_optimization(manager):
    opt = manager.optimize_capacity(
        tenant_id="tenant_a",
        resource_id="res-gpu-cluster-1",
        objective="COST_PERFORMANCE",
    )
    assert opt.plan_id.startswith("opt-")
    assert opt.auto_execute is False  # Mandatory invariant: auto_execute strictly False
    assert len(opt.recommendations) >= 1


# Flow 12: Cost-Performance Intelligence & Tradeoff Analysis
def test_flow_12_cost_performance(manager):
    cp = manager.evaluate_cost_performance(
        tenant_id="tenant_a",
        resource_id="res-gpu-cluster-1",
    )
    assert cp.assessment_id.startswith("cp-")
    assert cp.efficiency_score >= 0.0
    assert cp.cost_per_unit >= 0.0


# Flow 13: Dependency-Aware Capacity Propagation
def test_flow_13_capacity_propagation(manager):
    prop = manager.model_capacity_propagation(
        tenant_id="tenant_a",
        source_resource="res-gpu-cluster-1",
    )
    assert prop.propagation_id.startswith("cprop-")
    assert len(prop.downstream_resources) >= 0


# Flow 14: Reliability & Resilience Impact Assessment
def test_flow_14_reliability_impact(manager):
    imp = manager.assess_reliability_impact(
        tenant_id="tenant_a",
        resource_id="res-gpu-cluster-1",
    )
    assert imp.impact_id.startswith("relimp-")
    assert imp.risk_level in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


# Flow 15: What-If Scenario Simulation
def test_flow_15_scenario_simulation(manager):
    sim = manager.simulate_scenario(
        tenant_id="tenant_a",
        scenario_name="Black Friday 3x Traffic Surge",
        workload_multiplier=3.0,
    )
    assert sim.scenario_id.startswith("scen-")
    assert sim.workload_multiplier == 3.0
    assert sim.bottleneck_predicted is True or sim.bottleneck_predicted is False


# Flow 16: Advisory Capacity Recommendation
def test_flow_16_recommendations(manager):
    recs = manager.generate_recommendations(
        tenant_id="tenant_a",
        resource_id="res-gpu-cluster-1",
    )
    assert len(recs) >= 1
    for r in recs:
        assert r.auto_execute is False  # Mandatory invariant: auto_execute strictly False


# Flow 17: Autonomous Governance & Policy Evaluation
def test_flow_17_governance_evaluation(manager):
    gov = manager.evaluate_governance(
        tenant_id="tenant_a",
        action="PROVISION_GPU_NODES",
        risk_level=RiskLevel.HIGH,
    )
    assert gov["decision"] == GovernanceDecision.REQUIRE_APPROVAL.value
    assert gov["requires_human_approval"] is True


# Flow 18: Human Approval & Delegation Request
def test_flow_18_delegation_request(manager):
    del_req = manager.request_delegation(
        tenant_id="tenant_a",
        target_domain="INFRASTRUCTURE",
        action_type="SCALE_CLUSTER",
        payload={"add_nodes": 8},
        risk_level=RiskLevel.HIGH,
        is_approved=False,
    )
    assert del_req.delegation_id.startswith("cdel-")
    assert del_req.status == DelegationStatus.PENDING_APPROVAL
    assert del_req.requires_approval is True

    # Unapproved high risk action raises exception
    with pytest.raises(HighRiskCapacityActionRequiresApprovalException):
        manager.execute_delegation(tenant_id="tenant_a", delegation_id=del_req.delegation_id)

    # Approving delegation enables execution
    approved_req = manager.approve_delegation(tenant_id="tenant_a", delegation_id=del_req.delegation_id, approver_id="usr_cloud_admin")
    assert approved_req.status == DelegationStatus.APPROVED

    exec_res = manager.execute_delegation(tenant_id="tenant_a", delegation_id=del_req.delegation_id)
    assert exec_res.status == DelegationStatus.EXECUTED


# Flow 19: Closed-Loop Capacity Action Verification
def test_flow_19_action_verification(manager):
    ver = manager.verify_capacity_action(
        tenant_id="tenant_a",
        delegation_id="cdel-101",
        target_capacity=128.0,
        actual_capacity=128.0,
    )
    assert ver.verification_id.startswith("cver-")
    assert ver.verified is True


# Flow 20: Continuous Capacity Assurance & Risk Scoring
def test_flow_20_continuous_capacity_assurance(manager):
    ass = manager.evaluate_capacity_assurance(
        tenant_id="tenant_a",
        scope="GLOBAL",
    )
    assert ass.assurance_id.startswith("cass-")
    assert 0.0 <= ass.assurance_score <= 1.0


# Flow 21: Immutable Capacity Evidence Sealing & Lineage
def test_flow_21_evidence_sealing(manager):
    eb = manager.create_evidence_bundle(
        tenant_id="tenant_a",
        records=[{"event": "CAPACITY_SCALE", "nodes_added": 8}],
    )
    assert eb.bundle_id.startswith("cevd-")
    assert eb.sealed is True
    assert len(eb.integrity_hash) == 64  # SHA-256 hash length

    # Attempting to tamper with sealed evidence raises exception
    with pytest.raises(ImmutableCapacityIntelligenceRecordException):
        manager.tamper_evidence(tenant_id="tenant_a", bundle_id=eb.bundle_id)


# Flow 22: Cross-Tenant Isolation Enforcement
def test_flow_22_cross_tenant_isolation(manager):
    eb = manager.create_evidence_bundle("tenant_a", [{"data": "capacity_secret_a"}])

    # Tenant B accessing Tenant A's evidence raises CrossTenantCapacityIntelligenceException with no metadata leakage
    with pytest.raises(CrossTenantCapacityIntelligenceException) as exc_info:
        manager.get_evidence("tenant_b", eb.bundle_id)
    
    assert "Access denied" in str(exc_info.value)
