from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class RoutingStrategy(ABC):
    """Abstract strategy for selecting a provider for a routing request."""

    @abstractmethod
    async def determine_provider_name(self, *, model: Any, request: Any) -> str:
        """Return the provider name that should handle the request."""
        raise NotImplementedError
