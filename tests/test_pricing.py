from app.billing.cost_calculator import CostCalculator
from app.billing.models import PricingRule
from app.limits.models import UsageRecord


def test_cost_calculator_calculates_correctly():
    rule = PricingRule(
        provider="openai", model="gpt-4", input_cost_per_1k_tokens=0.03, output_cost_per_1k_tokens=0.06, currency="USD"
    )

    # Fake usage record with 10,000 total tokens
    # CostCalculator assumes 80% input, 20% output for now
    usage = UsageRecord(organization_id="org_1", provider="openai", model="gpt-4", total_tokens=10000, request_count=1)

    # 8,000 input tokens = (8000/1000) * 0.03 = 0.24
    # 2,000 output tokens = (2000/1000) * 0.06 = 0.12
    # Subtotal = 0.36
    breakdown = CostCalculator.calculate_cost(usage, rule)

    assert breakdown.input_cost == 0.24
    assert breakdown.output_cost == 0.12
    assert breakdown.subtotal == 0.36
    assert breakdown.total == 0.36


def test_cost_calculator_with_discounts_and_tax():
    rule = PricingRule(
        provider="test", model="test-model", input_cost_per_1k_tokens=1.0, output_cost_per_1k_tokens=1.0, currency="USD"
    )

    usage = UsageRecord(
        organization_id="org_1", provider="test", model="test-model", total_tokens=1000, request_count=1
    )

    # Total 1k tokens, split 80/20. So 1k * 1.0 = 1.0 total subtotal.
    # discount = 20%, tax = 10%
    # subtotal = 1.0
    # discount = 0.2
    # after discount = 0.8
    # tax = 0.08
    # total = 0.88

    breakdown = CostCalculator.calculate_cost(usage, rule, discount_pct=20.0, tax_pct=10.0)
    assert breakdown.subtotal == 1.0
    assert breakdown.discount == 0.2
    assert breakdown.tax == 0.08
    assert breakdown.total == 0.88
