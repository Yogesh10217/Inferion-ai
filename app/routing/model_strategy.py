from __future__ import annotations

from typing import TYPE_CHECKING

from app.routing.routing_strategy import RoutingStrategy

if TYPE_CHECKING:
    from app.registry.model_metadata import ModelMetadata
    from app.routing.request_router import RoutingRequest


class ModelBasedRoutingStrategy(RoutingStrategy):
    """Simple routing strategy that maps model identifiers to providers.

    This is intentionally lightweight and acts as the initial Phase 1 routing
    policy. It can be replaced later by cost-, latency-, or load-based policies
    without changing the router interface.
    """

    async def determine_provider_name(
        self, *, model: ModelMetadata | None, request: RoutingRequest | None = None
    ) -> str:
        if model is None:
            return "openai"

        model_id = getattr(model, "id", str(model))
        provider_name = getattr(model, "provider", None)
        if provider_name:
            return provider_name

        if str(model_id).startswith("gpt"):
            return "openai"
        if str(model_id).startswith("llama") or str(model_id).startswith("mistral"):
            return "ollama"
        return "openai"
