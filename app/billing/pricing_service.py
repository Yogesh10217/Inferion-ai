from typing import Optional

from sqlalchemy import select

from app.billing.models import PricingRule


class PricingService:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def get_rule_for_model(self, provider: str, model: str) -> Optional[PricingRule]:
        """Fetch the current pricing rule for a specific provider and model."""
        stmt = (
            select(PricingRule)
            .where(PricingRule.provider == provider, PricingRule.model == model)
            .order_by(PricingRule.effective_from.desc())
            .limit(1)
        )

        async with self.session_factory() as db:
            result = await db.execute(stmt)
            return result.scalars().first()

    async def get_all_rules(self) -> list[PricingRule]:
        """Fetch all pricing rules."""
        stmt = select(PricingRule)
        async with self.session_factory() as db:
            result = await db.execute(stmt)
            return list(result.scalars().all())

    async def seed_default_rules(self) -> None:
        """Seed example pricing rules if none exist."""
        rules = await self.get_all_rules()
        if rules:
            return

        examples = [
            PricingRule(
                provider="openai", model="gpt-4", input_cost_per_1k_tokens=0.03, output_cost_per_1k_tokens=0.06
            ),
            PricingRule(
                provider="openai",
                model="gpt-3.5-turbo",
                input_cost_per_1k_tokens=0.0015,
                output_cost_per_1k_tokens=0.002,
            ),
            PricingRule(
                provider="anthropic",
                model="claude-3-opus",
                input_cost_per_1k_tokens=0.015,
                output_cost_per_1k_tokens=0.075,
            ),
            PricingRule(
                provider="anthropic",
                model="claude-3-sonnet",
                input_cost_per_1k_tokens=0.003,
                output_cost_per_1k_tokens=0.015,
            ),
            PricingRule(
                provider="google",
                model="gemini-1.5-pro",
                input_cost_per_1k_tokens=0.0035,
                output_cost_per_1k_tokens=0.0105,
            ),
        ]

        async with self.session_factory() as db:
            db.add_all(examples)
            await db.commit()
