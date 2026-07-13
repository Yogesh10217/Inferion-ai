from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.registry.model_metadata import ModelMetadata
    from app.routing.request_router import RoutingRequest


class RoutingStrategy(ABC):
    """Abstract strategy for selecting a provider for a routing request."""

    @abstractmethod
    async def determine_provider_name(self, *, model: ModelMetadata | None, request: RoutingRequest | None = None) -> str:
        """Return the provider name that should handle the request."""
        raise NotImplementedError
