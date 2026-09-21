"""Unit tests for Subsystem Billing Adapters."""

from decimal import Decimal

from app.finops.cost_ledger import UnifiedCostLedger
from app.finops.integration import (
    DataFabricCostAdapter,
    ExtensionCostAdapter,
    GatewayCostAdapter,
    MLOpsCostAdapter,
    PlanningCostAdapter,
    ToolCostAdapter,
)


def test_all_subsystem_billing_adapters():
    ledger = UnifiedCostLedger()

    gw_adapter = GatewayCostAdapter(ledger=ledger)
    tool_adapter = ToolCostAdapter(ledger=ledger)
    plan_adapter = PlanningCostAdapter(ledger=ledger)
    ext_adapter = ExtensionCostAdapter(ledger=ledger)
    data_adapter = DataFabricCostAdapter(ledger=ledger)
    mlops_adapter = MLOpsCostAdapter(ledger=ledger)

    # 1. Gateway
    e_gw = gw_adapter.record_inference_cost("t_adapters", "openai", "gpt-3.5-turbo", 1000, 500)
    assert e_gw.component == "GATEWAY"

    # 2. Tool
    e_tool = tool_adapter.record_tool_cost("t_adapters", "web_search", Decimal("0.005"))
    assert e_tool.component == "TOOL"

    # 3. Planning
    e_plan = plan_adapter.record_planning_cost("t_adapters", "plan_1", Decimal("0.02"))
    assert e_plan.component == "PLANNING"

    # 4. Extension
    e_ext = ext_adapter.record_extension_cost("t_adapters", "ext_1", Decimal("0.01"))
    assert e_ext.component == "EXTENSION"

    # 5. Data Fabric
    e_data = data_adapter.record_data_cost("t_adapters", "ds_1", "INGESTION", Decimal("0.015"))
    assert e_data.component == "DATA_FABRIC"

    # 6. MLOps
    e_mlops = mlops_adapter.record_mlops_cost("t_adapters", "ast_1", "EVALUATION", Decimal("0.03"))
    assert e_mlops.component == "MLOPS"

    total = ledger.get_total_cost(tenant_id="t_adapters")
    assert total > Decimal("0.0")
