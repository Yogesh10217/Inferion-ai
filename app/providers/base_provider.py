from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator


@dataclass(slots=True)
class ProviderResponse:
    """Standardized response object returned by providers."""

    text: str
    model: str
    provider: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderModel:
    """Represents a model exposed by a provider."""

    id: str
    provider: str
    description: str = ""
    context_window: int | None = None
    status: str = "available"


class BaseProvider(ABC):
    """Abstract contract for inference providers."""

    name: str = "base"

    @abstractmethod
    async def generate(self, *, model: str, prompt: str, **kwargs: Any) -> ProviderResponse:
        """Generate a completion from the provider."""
        raise NotImplementedError

    @abstractmethod
    async def stream(self, *, model: str, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Stream text chunks from the provider."""
        raise NotImplementedError

    @abstractmethod
    async def health_check(self) -> bool:
        """Check whether the provider is healthy."""
        raise NotImplementedError

    @abstractmethod
    async def list_models(self) -> list[ProviderModel]:
        """List the models available from the provider."""
        raise NotImplementedError
