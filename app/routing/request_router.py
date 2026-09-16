from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.exceptions import ModelNotFoundException, RoutingException
from app.registry.model_registry import ModelRegistry
from app.routing.routing_strategy import RoutingStrategy


@dataclass(slots=True)
class RoutingRequest:
    """Minimal request object used by the request router."""

    model_id: str
    metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class RoutingDecision:
    """The result of a routing decision."""

    provider_id: str
    model_id: str
    metadata: dict[str, Any] = field(default_factory=dict)


class RequestRouter:
    """Routes a request to an abstract provider name using a pluggable strategy.

    The router is responsible only for routing decisions:
    - validate that the requested model exists
    - resolve model metadata from the registry
    - delegate provider selection to the strategy
    - return a RoutingDecision
    """

    def __init__(
        self,
        *,
        registry: ModelRegistry,
        strategy: RoutingStrategy,
    ) -> None:
        self._registry = registry
        self._strategy = strategy

    async def route(self, request: RoutingRequest) -> RoutingDecision:
        """Resolve the routing decision for the given request."""
        if not request.model_id:
            raise RoutingException("Model identifier is required")

        model = self._registry.get_model(request.model_id)
        if model is None:
            raise ModelNotFoundException(f"Model '{request.model_id}' was not found")

        try:
            provider_name = await self._strategy.determine_provider_name(model=model, request=request)
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise RoutingException("Routing strategy failed") from exc

        if not provider_name:
            raise RoutingException("Routing strategy did not return a provider name")

        return RoutingDecision(
            provider_id=provider_name,
            model_id=request.model_id,
            metadata=model.metadata or {},
        )
