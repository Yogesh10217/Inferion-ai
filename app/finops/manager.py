"""Master Coordinator for FinOps Platform."""

import logging
from typing import Any, Dict

from app.finops.analytics import CostAnalyticsEngine
from app.finops.anomaly_detection import CostAnomalyDetector
from app.finops.attribution import CostAttributionEngine
from app.finops.budgets import BudgetManager
from app.finops.capacity import CapacityPlanner
from app.finops.chargeback import ChargebackManager
from app.finops.cost_ledger import UnifiedCostLedger
from app.finops.forecasting import CostForecastingEngine
from app.finops.governance import FinOpsGovernanceEngine
from app.finops.integration import (
    DataFabricCostAdapter,
    ExtensionCostAdapter,
    GatewayCostAdapter,
    MLOpsCostAdapter,
    PlanningCostAdapter,
    ToolCostAdapter,
)
from app.finops.observability import FinOpsMetricsCollector
from app.finops.optimization import CostOptimizationEngine
from app.finops.pricing import PricingManager
from app.finops.savings import SavingsVerificationEngine

logger = logging.getLogger(__name__)


class FinOpsManager:
    """Master Coordinator unifying Unified Cost Ledger, Attribution, Budgets, Analytics, Forecasting, Anomaly Detection, Optimization, Governance, Capacity Planning, Savings Verification, Chargeback, Pricing, Observability, and Subsystem Adapters."""

    def __init__(self) -> None:
        self.cost_ledger = UnifiedCostLedger()
        self.pricing_manager = PricingManager()
        self.attribution_engine = CostAttributionEngine(ledger=self.cost_ledger)
        self.budget_manager = BudgetManager()
        self.analytics_engine = CostAnalyticsEngine(ledger=self.cost_ledger)
        self.forecasting_engine = CostForecastingEngine(ledger=self.cost_ledger)
        self.anomaly_detector = CostAnomalyDetector()
        self.optimization_engine = CostOptimizationEngine()
        self.governance_engine = FinOpsGovernanceEngine()
        self.capacity_planner = CapacityPlanner()
        self.savings_verifier = SavingsVerificationEngine()
        self.chargeback_manager = ChargebackManager(ledger=self.cost_ledger)
        self.metrics_collector = FinOpsMetricsCollector()

        # Adapters
        self.gateway_adapter = GatewayCostAdapter(ledger=self.cost_ledger, pricing_manager=self.pricing_manager)
        self.tool_adapter = ToolCostAdapter(ledger=self.cost_ledger)
        self.planning_adapter = PlanningCostAdapter(ledger=self.cost_ledger)
        self.extension_adapter = ExtensionCostAdapter(ledger=self.cost_ledger)
        self.data_fabric_adapter = DataFabricCostAdapter(ledger=self.cost_ledger)
        self.mlops_adapter = MLOpsCostAdapter(ledger=self.cost_ledger)

        logger.info(
            "[FINOPS MANAGER] Master FinOpsManager initialized with all 15 financial intelligence domain subsystems and adapters"
        )

    def record_usage_cost(
        self,
        tenant_id: str,
        resource_id: str,
        cost_amount: float,
        category: str = "MODEL_USAGE",
    ) -> Any:
        return self.cost_ledger.record_entry(
            tenant_id=tenant_id,
            resource_id=resource_id,
            amount=cost_amount,
            category=category,
        )

    def get_summary(self) -> Dict[str, Any]:
        total_cost = self.cost_ledger.get_total_cost()
        return {
            "total_ledger_cost": str(total_cost),
            "registered_budgets": len(self.budget_manager.list_budgets()),
            "anomalies_detected": len(self.anomaly_detector.list_anomalies()),
            "metrics": self.metrics_collector.get_summary(),
        }
