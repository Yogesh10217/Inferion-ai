"""Mandatory 20 E2E Integration Flow Tests for FinOps Intelligence Platform (Phase 5.42)."""

import pytest

from app.finops_intelligence.allocation import AllocationDimension, AllocationRule
from app.finops_intelligence.anomalies import CostAnomalyType
from app.finops_intelligence.budgets import BudgetStatus
from app.finops_intelligence.cost_intelligence import CostCategory
from app.finops_intelligence.delegation import FinOpsDelegationAction
from app.finops_intelligence.exceptions import (
    CrossTenantFinOpsIntelligenceException,
    HighRiskOptimizationRequiresApprovalException,
    ImmutableFinOpsRecordException,
)
from app.finops_intelligence.manager import FinOpsIntelligenceManager
from app.finops_intelligence.optimization import OptimizationType
from app.finops_intelligence.usage import UsageMetric


@pytest.fixture
def manager():
    return FinOpsIntelligenceManager()


def test_flow_01_cost_recording_and_aggregation(manager):
    manager.cost_manager.record_cost("tenant_a", CostCategory.MODEL_INFERENCE, 100.0)
    manager.cost_manager.record_cost("tenant_a", CostCategory.MODEL_INFERENCE, 250.0)
    agg = manager.cost_manager.aggregate_costs("tenant_a", CostCategory.MODEL_INFERENCE)
    assert agg.total_cost_usd == 350.0
    assert agg.record_count == 2


def test_flow_02_tenant_cost_isolation(manager):
    rec = manager.cost_manager.record_cost("tenant_a", CostCategory.MODEL_INFERENCE, 100.0)
    manager.cost_repo.save(rec)

    with pytest.raises(CrossTenantFinOpsIntelligenceException) as exc_info:
        manager.cost_repo.get("tenant_b", rec.record_id)
    assert "Access denied." in str(exc_info.value)
    assert rec.record_id not in str(exc_info.value)
    assert "tenant_a" not in str(exc_info.value)


def test_flow_03_usage_intelligence(manager):
    metric1 = UsageMetric(metric_name="TOKENS", metric_value=100000.0)
    metric2 = UsageMetric(metric_name="API_CALLS", metric_value=50.0)
    manager.usage_manager.record_usage("tenant_a", "MODEL", "model_gpt4", [metric1, metric2])

    asm = manager.usage_manager.evaluate_usage("tenant_a")
    assert asm.total_tokens == 100000.0
    assert asm.total_api_calls == 50.0


def test_flow_04_cost_allocation(manager):
    rec = manager.cost_manager.record_cost("tenant_a", CostCategory.INFRASTRUCTURE, 1000.0)
    rule1 = AllocationRule(dimension=AllocationDimension.TEAM, target_entity="TeamAlpha", percentage=60.0)
    rule2 = AllocationRule(dimension=AllocationDimension.TEAM, target_entity="TeamBeta", percentage=40.0)

    results = manager.allocation_manager.allocate_cost("tenant_a", rec.record_id, 1000.0, [rule1, rule2])
    assert len(results) == 2
    assert results[0].allocated_amount_usd == 600.0
    assert results[1].allocated_amount_usd == 400.0


def test_flow_05_budget_threshold_warning(manager):
    bdg = manager.budget_manager.create_budget(
        "tenant_a", "Monthly Budget", amount_usd=1000.0, warning_threshold_pct=75.0
    )
    asm = manager.budget_manager.evaluate_budget("tenant_a", bdg.budget_id, current_spend_usd=800.0)
    assert asm.status == BudgetStatus.WARNING
    assert asm.utilization_pct == 80.0
    assert not asm.requires_escalation


def test_flow_06_budget_critical_threshold(manager):
    bdg = manager.budget_manager.create_budget(
        "tenant_a", "Monthly Budget", amount_usd=1000.0, critical_threshold_pct=90.0
    )
    asm = manager.budget_manager.evaluate_budget("tenant_a", bdg.budget_id, current_spend_usd=950.0)
    assert asm.status == BudgetStatus.CRITICAL
    assert asm.requires_escalation


def test_flow_07_spending_forecast(manager):
    fcst = manager.forecast_manager.generate_forecast("tenant_a", [1000.0, 1200.0, 1100.0])
    assert fcst.projected_spend_usd == 1100.0
    assert fcst.confidence.value == "HIGH"


def test_flow_08_cost_anomaly_detection(manager):
    anom = manager.anomaly_manager.detect_anomaly(
        "tenant_a", "res_gpu_1", expected_amount_usd=100.0, actual_amount_usd=350.0
    )
    assert anom is not None
    assert anom.anomaly_type == CostAnomalyType.SPENDING_SPIKE
    assert anom.deviation_pct == 250.0
    assert anom.severity.value == "CRITICAL"


def test_flow_09_runaway_agent_cost_detection(manager):
    anom = manager.anomaly_manager.detect_anomaly(
        "tenant_a",
        "agent_executor_99",
        expected_amount_usd=50.0,
        actual_amount_usd=200.0,
        anomaly_type=CostAnomalyType.RUNAWAY_AGENT_COST,
    )
    assert anom is not None
    assert anom.anomaly_type == CostAnomalyType.RUNAWAY_AGENT_COST


def test_flow_10_optimization_recommendation(manager):
    opt = manager.optimization_manager.create_recommendation(
        "tenant_a",
        "res_cluster_01",
        OptimizationType.MODEL_RIGHTSIZING,
        estimated_monthly_savings_usd=500.0,
        action_summary="Switch to quantized 8-bit model",
    )
    assert opt.status.value == "PROPOSED"
    assert opt.estimated_monthly_savings_usd == 500.0


def test_flow_11_least_cost_efficient_model_recommendation(manager):
    asm = manager.efficiency_manager.evaluate_efficiency("tenant_a", "model_fp32_heavy", model_efficiency_score=50.0)
    assert asm.overall_efficiency_score < 70.0
    assert len(asm.recommendations) == 1
    assert "Model Rightsizing" in asm.recommendations[0].title


def test_flow_12_high_risk_optimization_requires_approval(manager):
    action = FinOpsDelegationAction(
        action_type="TERMINATE_IDLE_WORKLOAD", target_resource_id="prod_db_primary", is_high_risk=True
    )
    plan = manager.delegation_manager.create_delegation_plan("tenant_a", "opt_123", [action])
    assert plan.requires_approval

    with pytest.raises(HighRiskOptimizationRequiresApprovalException):
        manager.delegation_manager.execute_delegation("tenant_a", plan.plan_id)


def test_flow_13_delegation_only_optimization_execution(manager):
    action = FinOpsDelegationAction(
        action_type="DOWNSIZE_RESOURCE", target_resource_id="res_node_12", is_high_risk=False
    )
    plan = manager.delegation_manager.create_delegation_plan("tenant_a", "opt_456", [action])
    del_req = manager.delegation_manager.execute_delegation("tenant_a", plan.plan_id)
    assert del_req.delegation_id.startswith("delreq_")
    assert del_req.target.value == "PLATFORM_OPERATIONS"


def test_flow_14_financial_risk_evaluation(manager):
    risk_asm = manager.risk_manager.evaluate_risk(
        "tenant_a", "dept_engineering", budget_risk_score=90.0, forecast_risk_score=85.0
    )
    assert risk_asm.profile.overall_risk_score == 61.67
    assert risk_asm.profile.risk_level == "HIGH"


def test_flow_15_sensitive_data_redaction(manager):
    metric = UsageMetric(metric_name="TOKENS", metric_value=100.0)
    rec = manager.usage_manager.record_usage(
        "tenant_a",
        "MODEL",
        "mod_1",
        [metric],
        {"api_key": "sk-secret-123456", "user_email": "alice@example.com"},
    )
    assert "api_key" not in rec.sanitized_metadata or rec.sanitized_metadata["api_key"] == "[REDACTED]"


def test_flow_16_immutable_financial_evidence(manager):
    bundle = manager.evidence_manager.create_bundle("tenant_a", "Financial Audit Bundle")
    manager.evidence_manager.add_evidence("tenant_a", bundle.bundle_id, "COST_RECORD", "c_1", {"amt": 100})
    finalized = manager.evidence_manager.finalize_bundle("tenant_a", bundle.bundle_id)
    assert finalized.sha256_hash is not None

    with pytest.raises(ImmutableFinOpsRecordException):
        manager.evidence_manager.add_evidence("tenant_a", bundle.bundle_id, "COST_RECORD", "c_2", {"amt": 200})


def test_flow_17_investigation_snapshot(manager):
    inv = manager.investigation_manager.open_investigation("tenant_a", "Investigation into GPU Cost Spike")
    manager.investigation_manager.start_investigating("tenant_a", inv.investigation_id)
    concluded = manager.investigation_manager.conclude_investigation("tenant_a", inv.investigation_id)
    assert concluded.is_concluded
    assert concluded.snapshot_id is not None


def test_flow_18_learning_does_not_auto_execute(manager):
    lrn = manager.learning_manager.record_learning(
        "tenant_a",
        "UnusedReservations",
        "Reservations idling over weekends",
        "Schedule shutdown",
        "Downsize cluster on Friday night",
        "cluster_main",
    )
    assert lrn.recommendations[0].auto_execute is False


def test_flow_19_cross_platform_cost_attribution(manager):
    event = manager.billing_tracker.record_cost_event("tenant_a", "INTEGRATION_INTELLIGENCE", 25.5)
    assert event.amount_usd == 25.5
    assert manager.billing_tracker.get_tenant_total_spend("tenant_a") == 25.5


def test_flow_20_full_enterprise_finops_lifecycle(manager):
    res = manager.run_full_lifecycle("tenant_a", "res_compute_prod_99", amount_usd=1500.0)
    assert res["status"] == "COMPLETED"
    assert res["budget_status"] == "EXCEEDED"
    assert res["governance_status"] in ["ALLOW", "RESTRICT", "REQUIRE_APPROVAL", "DENY", "BLOCK"]
    assert res["snapshot_id"] is not None
    assert res["evidence_sha256"] is not None
    assert res["learning_auto_execute"] is False
