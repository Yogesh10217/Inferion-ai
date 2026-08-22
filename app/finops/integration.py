"""Subsystem Cost Adapters normalizing cost signals into the Unified Cost Ledger."""

from decimal import Decimal
import logging
from typing import Dict, Any, Optional

from app.finops.cost_ledger import UnifiedCostLedger, CostCategory, CostLedgerEntry
from app.finops.pricing import PricingManager

# Imports of existing subsystem billing trackers
from app.billing.tracker import tracker as gateway_tracker
from app.tools.tool_billing import ToolBillingTracker
from app.planning.planning_billing import PlanningBillingTracker
from app.extensions.billing import ExtensionBillingTracker
from app.data_fabric.billing import DataFabricBillingTracker
from app.mlops.billing import MLOpsBillingTracker

logger = logging.getLogger(__name__)


class GatewayCostAdapter:
    """Adapts AI Gateway model inference token usage to the Unified Cost Ledger using versioned pricing."""

    def __init__(self, ledger: UnifiedCostLedger, pricing_manager: Optional[PricingManager] = None) -> None:
        self.ledger = ledger
        self.pricing_manager = pricing_manager or PricingManager()

    def record_inference_cost(
        self,
        tenant_id: str,
        provider: str,
        model_id: str,
        prompt_tokens: int,
        completion_tokens: int,
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> CostLedgerEntry:
        total_tokens = prompt_tokens + completion_tokens
        unit_price = self.pricing_manager.get_pricing(provider, model_id).input_token_price_per_1k
        cost = self.pricing_manager.calculate_token_cost(provider, model_id, prompt_tokens, completion_tokens)

        # Update gateway tracker
        gateway_tracker.track_embedding_tokens(total_tokens)

        return self.ledger.record_cost(
            component="GATEWAY",
            cost_category=CostCategory.MODEL_INFERENCE,
            quantity=Decimal(str(total_tokens)),
            unit_price=unit_price,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            provider=provider,
            model_id=model_id,
            unit="tokens",
            metadata={"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens},
        )


class ToolCostAdapter:
    def __init__(self, ledger: UnifiedCostLedger, tool_tracker: Optional[ToolBillingTracker] = None) -> None:
        self.ledger = ledger
        self.tool_tracker = tool_tracker or ToolBillingTracker()

    def record_tool_cost(self, tenant_id: str, tool_name: str, cost: Decimal) -> CostLedgerEntry:
        return self.ledger.record_cost(
            component="TOOL",
            cost_category=CostCategory.TOOL_EXECUTION,
            quantity=Decimal("1.0"),
            unit_price=cost,
            tenant_id=tenant_id,
            resource_id=tool_name,
        )


class PlanningCostAdapter:
    def __init__(self, ledger: UnifiedCostLedger, planning_tracker: Optional[PlanningBillingTracker] = None) -> None:
        self.ledger = ledger
        self.planning_tracker = planning_tracker or PlanningBillingTracker()

    def record_planning_cost(self, tenant_id: str, plan_id: str, cost: Decimal) -> CostLedgerEntry:
        return self.ledger.record_cost(
            component="PLANNING",
            cost_category=CostCategory.PLANNING,
            quantity=Decimal("1.0"),
            unit_price=cost,
            tenant_id=tenant_id,
            resource_id=plan_id,
        )


class ExtensionCostAdapter:
    def __init__(self, ledger: UnifiedCostLedger, extension_tracker: Optional[ExtensionBillingTracker] = None) -> None:
        self.ledger = ledger
        self.extension_tracker = extension_tracker or ExtensionBillingTracker()

    def record_extension_cost(self, tenant_id: str, extension_id: str, cost: Decimal) -> CostLedgerEntry:
        return self.ledger.record_cost(
            component="EXTENSION",
            cost_category=CostCategory.EXTENSION_EXECUTION,
            quantity=Decimal("1.0"),
            unit_price=cost,
            tenant_id=tenant_id,
            resource_id=extension_id,
        )


class DataFabricCostAdapter:
    def __init__(self, ledger: UnifiedCostLedger, data_tracker: Optional[DataFabricBillingTracker] = None) -> None:
        self.ledger = ledger
        self.data_tracker = data_tracker or DataFabricBillingTracker()

    def record_data_cost(self, tenant_id: str, source_id: str, operation: str, cost: Decimal) -> CostLedgerEntry:
        return self.ledger.record_cost(
            component="DATA_FABRIC",
            cost_category=CostCategory.DATA_INGESTION if "INGEST" in operation.upper() else CostCategory.DATA_STORAGE,
            quantity=Decimal("1.0"),
            unit_price=cost,
            tenant_id=tenant_id,
            resource_id=source_id,
        )


class MLOpsCostAdapter:
    def __init__(self, ledger: UnifiedCostLedger, mlops_tracker: Optional[MLOpsBillingTracker] = None) -> None:
        self.ledger = ledger
        self.mlops_tracker = mlops_tracker or MLOpsBillingTracker()

    def record_mlops_cost(self, tenant_id: str, asset_id: str, operation: str, cost: Decimal) -> CostLedgerEntry:
        return self.ledger.record_cost(
            component="MLOPS",
            cost_category=CostCategory.EVALUATION if "EVAL" in operation.upper() else CostCategory.DEPLOYMENT,
            quantity=Decimal("1.0"),
            unit_price=cost,
            tenant_id=tenant_id,
            resource_id=asset_id,
        )
