"""Versioned Pricing Catalog Subsystem with Decimal Precision."""

import logging
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict

from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PricingEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: f"price_{uuid.uuid4().hex[:10]}")
    provider: str
    model_id: str
    pricing_version: str = "1.0.0"

    input_token_price_per_1k: Decimal = Field(default=Decimal("0.0015"))
    output_token_price_per_1k: Decimal = Field(default=Decimal("0.0020"))
    compute_price_per_second: Decimal = Field(default=Decimal("0.0001"))

    effective_at: datetime = Field(default_factory=_now)

    @field_validator("input_token_price_per_1k", "output_token_price_per_1k", "compute_price_per_second", mode="before")
    @classmethod
    def parse_decimal(cls, value: Any) -> Decimal:
        if isinstance(value, float):
            return Decimal(str(value))
        return Decimal(value)


class PricingManager:
    """Manages versioned provider/model pricing tables without mutating historical cost entries."""

    def __init__(self) -> None:
        self._pricing: Dict[str, PricingEntry] = {
            "openai:gpt-4": PricingEntry(provider="openai", model_id="gpt-4", input_token_price_per_1k=Decimal("0.03"), output_token_price_per_1k=Decimal("0.06")),
            "openai:gpt-3.5-turbo": PricingEntry(provider="openai", model_id="gpt-3.5-turbo", input_token_price_per_1k=Decimal("0.0015"), output_token_price_per_1k=Decimal("0.002")),
            "internal:default": PricingEntry(provider="internal", model_id="default", input_token_price_per_1k=Decimal("0.001"), output_token_price_per_1k=Decimal("0.001")),
        }

    def register_pricing(self, provider: str, model_id: str, input_price: Decimal, output_price: Decimal, version: str = "1.0.0") -> PricingEntry:
        in_p = Decimal(str(input_price)) if isinstance(input_price, (float, int, str)) else input_price
        out_p = Decimal(str(output_price)) if isinstance(output_price, (float, int, str)) else output_price

        entry = PricingEntry(
            provider=provider,
            model_id=model_id,
            pricing_version=version,
            input_token_price_per_1k=in_p,
            output_token_price_per_1k=out_p,
        )
        key = f"{provider}:{model_id}"
        self._pricing[key] = entry
        logger.info(f"[PRICING MANAGER] Registered pricing for '{key}' (v{version}): Input = ${in_p}/1k, Output = ${out_p}/1k")
        return entry

    def get_pricing(self, provider: str, model_id: str) -> PricingEntry:
        key = f"{provider}:{model_id}"
        if key in self._pricing:
            return self._pricing[key]
        return self._pricing.get("internal:default", PricingEntry(provider="internal", model_id="default"))

    def calculate_token_cost(self, provider: str, model_id: str, prompt_tokens: int, completion_tokens: int) -> Decimal:
        pricing = self.get_pricing(provider, model_id)
        p_cost = (Decimal(str(prompt_tokens)) / Decimal("1000.0")) * pricing.input_token_price_per_1k
        c_cost = (Decimal(str(completion_tokens)) / Decimal("1000.0")) * pricing.output_token_price_per_1k
        return (p_cost + c_cost).quantize(Decimal("0.000001"))
