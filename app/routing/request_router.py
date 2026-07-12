from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.core.exceptions import ModelNotFoundException, ProviderNotFoundException, RoutingException
from app.providers.base_provider import BaseProvider
from app.providers.provider_factory import ProviderFactory
from app.registry.model_registry import ModelRegistry
from app.routing.routing_strategy import RoutingStrategy


@dataclass(slots=True)
class RoutingRequest:
    """Minimal request object used by the request router."""

    model_id: str
    metadata: dict[str, Any] | None = None


class RequestRouter:
    """Routes a request to an appropriate provider using a pluggable strategy.

    The router is responsible only for routing decisions:
    - validate that the requested model exists
    - resolve model metadata from the registry
    - delegate provider selection to the strategy
    - ask the provider factory for the Provider instance
    - return the provider to the caller
    """

    def __init__(
        self,
        *,
        registry: ModelRegistry,
        strategy: RoutingStrategy,
        provider_factory: ProviderFactory | None = None,
    ) -> None:
        self._registry = registry
        self._strategy = strategy
        self._provider_factory = provider_factory or ProviderFactory()

    async def route(self, request: RoutingRequest) -> BaseProvider:
        """Resolve the provider for the given routing request."""
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

        if not self._provider_factory.provider_exists(provider_name):
            raise ProviderNotFoundException(f"Provider '{provider_name}' was not found")

        try:
            provider = self._provider_factory.get_provider(provider_name)
        except Exception as exc:  # pragma: no cover - defensive boundary
            raise ProviderNotFoundException(f"Provider '{provider_name}' could not be instantiated") from exc

        return provider
