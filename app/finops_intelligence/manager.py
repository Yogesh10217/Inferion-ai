"""Master Orchestrator for FinOps Intelligence Platform (Phase 5.42)."""

from typing import Any, Dict

from app.finops_intelligence.allocation import AllocationDimension, AllocationRule, CostAllocationManager
from app.finops_intelligence.analytics import FinOpsAnalyticsEngine
from app.finops_intelligence.anomalies import CostAnomalyManager, CostAnomalyType
from app.finops_intelligence.billing import FinOpsBillingTracker
from app.finops_intelligence.budgets import BudgetManager
from app.finops_intelligence.chargeback import ChargebackManager
from app.finops_intelligence.commitments import CommitmentManager
from app.finops_intelligence.cost_intelligence import CostCategory, CostDimension, CostIntelligenceManager
from app.finops_intelligence.delegation import FinOpsDelegationAction, FinOpsDelegationManager
from app.finops_intelligence.efficiency import ResourceEfficiencyManager
from app.finops_intelligence.evidence import FinOpsEvidenceManager
from app.finops_intelligence.forecasting import ForecastManager, ForecastScenario
from app.finops_intelligence.governance import FinOpsGovernanceEngine
from app.finops_intelligence.investigations import FinOpsInvestigationManager
from app.finops_intelligence.learning import FinOpsLearningManager
from app.finops_intelligence.observability import FinOpsMetricsCollector
from app.finops_intelligence.optimization import CostOptimizationManager, OptimizationType
from app.finops_intelligence.repositories import (
    AllocationRepository,
    BudgetRepository,
    CostRepository,
    InvestigationRepository,
    OptimizationRepository,
)
from app.finops_intelligence.risk import FinOpsRiskManager
from app.finops_intelligence.showback import ShowbackManager
from app.finops_intelligence.snapshots import FinOpsSnapshotManager
from app.finops_intelligence.trust import FinOpsTrustEngine
from app.finops_intelligence.unit_economics import UnitEconomicManager
from app.finops_intelligence.usage import UsageIntelligenceManager, UsageMetric
from app.finops_intelligence.verification import FinOpsVerificationManager, VerificationCheck


class FinOpsIntelligenceManager:
    """Master orchestrator for Enterprise AI FinOps Intelligence Platform."""

    def __init__(self) -> None:
        self.cost_manager = CostIntelligenceManager()
        self.usage_manager = UsageIntelligenceManager()
        self.allocation_manager = CostAllocationManager()
        self.budget_manager = BudgetManager()
        self.forecast_manager = ForecastManager()
        self.anomaly_manager = CostAnomalyManager()
        self.optimization_manager = CostOptimizationManager()
        self.efficiency_manager = ResourceEfficiencyManager()
        self.unit_economics_manager = UnitEconomicManager()
        self.chargeback_manager = ChargebackManager()
        self.showback_manager = ShowbackManager()
        self.commitment_manager = CommitmentManager()
        self.governance_engine = FinOpsGovernanceEngine()
        self.risk_manager = FinOpsRiskManager()
        self.delegation_manager = FinOpsDelegationManager()
        self.verification_manager = FinOpsVerificationManager()
        self.evidence_manager = FinOpsEvidenceManager()
        self.investigation_manager = FinOpsInvestigationManager()
        self.snapshot_manager = FinOpsSnapshotManager()
        self.trust_engine = FinOpsTrustEngine()
        self.learning_manager = FinOpsLearningManager()
        self.analytics_engine = FinOpsAnalyticsEngine()
        self.metrics_collector = FinOpsMetricsCollector()
        self.billing_tracker = FinOpsBillingTracker()

        # Repositories
        self.cost_repo = CostRepository()
        self.budget_repo = BudgetRepository()
        self.allocation_repo = AllocationRepository()
        self.optimization_repo = OptimizationRepository()
        self.investigation_repo = InvestigationRepository()

    def run_full_lifecycle(
        self,
        tenant_id: str,
        resource_id: str,
        amount_usd: float = 1200.0,
    ) -> Dict[str, Any]:
        """Runs the complete end-to-end governed financial intelligence lifecycle."""
        # 1. Record Usage & Cost
        metric = UsageMetric(metric_name="TOKENS", metric_value=500000.0)
        self.usage_manager.record_usage(tenant_id, "MODEL", resource_id, [metric], {"env": "prod"})

        cost_rec = self.cost_manager.record_cost(
            tenant_id=tenant_id,
            category=CostCategory.MODEL_INFERENCE,
            amount_usd=amount_usd,
            dimensions=[CostDimension(key="env", value="prod")],
        )
        self.cost_repo.save(cost_rec)
        self.metrics_collector.increment("cost_total", amount_usd)

        # 2. Allocate Spend
        rule = AllocationRule(dimension=AllocationDimension.TEAM, target_entity="DataScience", percentage=100.0)
        alloc_results = self.allocation_manager.allocate_cost(tenant_id, cost_rec.record_id, amount_usd, [rule])

        # 3. Budget & Forecast
        bdg = self.budget_manager.create_budget(tenant_id, "Monthly AIBudget", amount_usd=1000.0)
        self.budget_repo.save(bdg)
        bdg_asm = self.budget_manager.evaluate_budget(tenant_id, bdg.budget_id, amount_usd)
        self.metrics_collector.set_gauge("budget_utilization", bdg_asm.utilization_pct)

        fcst = self.forecast_manager.generate_forecast(tenant_id, [800.0, 950.0, amount_usd], ForecastScenario.BASELINE)

        # 4. Anomaly Detection & Optimization
        anomaly = self.anomaly_manager.detect_anomaly(tenant_id, resource_id, expected_amount_usd=500.0, actual_amount_usd=amount_usd, anomaly_type=CostAnomalyType.SPENDING_SPIKE)
        if anomaly:
            self.metrics_collector.increment("anomalies_total")

        opt_rec = self.optimization_manager.create_recommendation(
            tenant_id=tenant_id,
            target_resource_id=resource_id,
            optimization_type=OptimizationType.MODEL_RIGHTSIZING,
            estimated_monthly_savings_usd=400.0,
            action_summary="Rightsize to quantized model variant",
            is_high_risk=False,
        )
        self.optimization_repo.save(opt_rec)
        self.metrics_collector.increment("optimization_recommendations")

        # 5. Risk & Governance Evaluation
        risk_asm = self.risk_manager.evaluate_risk(tenant_id, resource_id, budget_risk_score=85.0)
        gov_dec = self.governance_engine.evaluate_governance(tenant_id, "MODEL_RIGHTSIZING", risk_score=risk_asm.profile.overall_risk_score)

        # 6. Delegation & Verification
        action = FinOpsDelegationAction(action_type="DOWNSIZE_RESOURCE", target_resource_id=resource_id, is_high_risk=False)
        del_plan = self.delegation_manager.create_delegation_plan(tenant_id, opt_rec.optimization_id, [action])
        del_req = self.delegation_manager.execute_delegation(tenant_id, del_plan.plan_id)

        v_chk = VerificationCheck(check_name="Verify Resource Downsize", passed=True, details="Resource downsized successfully")
        verif = self.verification_manager.verify_action(tenant_id, del_plan.plan_id, [v_chk])

        # 7. Investigation & Snapshot
        inv = self.investigation_manager.open_investigation(tenant_id, f"Investigation for {resource_id}", target_anomaly_id=anomaly.anomaly_id if anomaly else None)
        self.investigation_manager.start_investigating(tenant_id, inv.investigation_id)
        self.investigation_manager.record_finding(tenant_id, inv.investigation_id, "Unoptimized prompt tokens")
        concluded_inv = self.investigation_manager.conclude_investigation(tenant_id, inv.investigation_id)
        self.investigation_repo.save(concluded_inv)

        snap = self.snapshot_manager.capture_snapshot(tenant_id, concluded_inv.investigation_id, "FINOPS_INVESTIGATION", concluded_inv.model_dump(mode="json"))

        # 8. Evidence & Learning
        bundle = self.evidence_manager.create_bundle(tenant_id, f"Evidence for {resource_id}")
        self.evidence_manager.add_evidence(tenant_id, bundle.bundle_id, "COST_LEDGER_ENTRY", cost_rec.record_id, {"raw": "cost payload"})
        finalized_bundle = self.evidence_manager.finalize_bundle(tenant_id, bundle.bundle_id)

        learning = self.learning_manager.record_learning(
            tenant_id=tenant_id,
            pattern_name="TokenBurstPattern",
            description="High prompt token usage during batch jobs",
            recommendation_title="Enable prompt caching",
            suggested_optimization="Use prompt cache headers",
            target_resource_id=resource_id,
        )

        # 9. Analytics & Billing
        self.billing_tracker.record_cost_event(tenant_id, "FINOPS_INTELLIGENCE", 0.01)
        report = self.analytics_engine.generate_report(tenant_id, total_spend_usd=amount_usd, budget_utilization_pct=bdg_asm.utilization_pct, potential_savings_usd=400.0)

        return {
            "status": "COMPLETED",
            "cost_record_id": cost_rec.record_id,
            "budget_status": bdg_asm.status.value,
            "delegation_id": del_req.delegation_id,
            "governance_status": gov_dec.status.value,
            "snapshot_id": snap.snapshot_id,
            "evidence_sha256": finalized_bundle.sha256_hash,
            "learning_auto_execute": learning.recommendations[0].auto_execute,
        }
