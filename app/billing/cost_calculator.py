from app.billing.models import PricingRule
from app.billing.schemas import CostBreakdown
from app.limits.models import UsageRecord


class CostCalculator:
    @staticmethod
    def calculate_cost(
        usage: UsageRecord, rule: PricingRule, discount_pct: float = 0.0, tax_pct: float = 0.0
    ) -> CostBreakdown:
        """Calculate the cost of a single usage record."""
        # Note: UsageRecord might not track input vs output tokens natively in Phase 3.3.
        # If total tokens is all we have, we'll apply an average or        # For simplicity, if we don't have separate input/output tokens in UsageRecord
        # Let's assume usage.total_tokens is the total tokens.
        # We can simulate an 80/20 split for input/output.
        total_tokens = usage.total_tokens

        # In a real system, UsageRecord should track input/output separately.
        # Since Phase 3.3 usage record only has `tokens`, we split 50/50 for demonstration
        # or use input_cost if it's prompt-heavy.
        input_tokens = total_tokens * 0.8
        output_tokens = total_tokens * 0.2

        input_cost = (input_tokens / 1000.0) * rule.input_cost_per_1k_tokens
        output_cost = (output_tokens / 1000.0) * rule.output_cost_per_1k_tokens

        subtotal = input_cost + output_cost
        discount = subtotal * (discount_pct / 100.0)
        after_discount = subtotal - discount
        tax = after_discount * (tax_pct / 100.0)
        total = after_discount + tax

        return CostBreakdown(
            input_cost=round(input_cost, 6),
            output_cost=round(output_cost, 6),
            subtotal=round(subtotal, 6),
            discount=round(discount, 6),
            tax=round(tax, 6),
            total=round(total, 6),
            currency=rule.currency,
        )
