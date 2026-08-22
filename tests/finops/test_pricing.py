"""Unit tests for PricingManager and Versioned Pricing Catalog."""

from decimal import Decimal
import pytest
from app.finops.pricing import PricingManager


def test_versioned_pricing_calculation():
    mgr = PricingManager()

    # Calculate token cost for GPT-4 (30k prompt, 10k completion)
    cost = mgr.calculate_token_cost("openai", "gpt-4", prompt_tokens=1000, completion_tokens=1000)
    assert cost == Decimal("0.090000")  # (1 * 0.03) + (1 * 0.06)

    # Register updated pricing v2 does not alter default lookup until registered
    mgr.register_pricing("openai", "gpt-4-turbo", input_price=Decimal("0.01"), output_price=Decimal("0.03"), version="2.0.0")
    cost_v2 = mgr.calculate_token_cost("openai", "gpt-4-turbo", prompt_tokens=1000, completion_tokens=1000)
    assert cost_v2 == Decimal("0.040000")
