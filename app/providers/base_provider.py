from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

from app.schemas.inference_response import InferenceResponse
from app.schemas.request import InferenceRequest


@dataclass(slots=True)
class ProviderResponse:
    """Backward-compatible response object returned by providers."""

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
    async def generate(self, *, request: InferenceRequest | None = None, model: str | None = None, prompt: str | None = None, **kwargs: Any) -> InferenceResponse:
        """Generate a completion from the provider and return a normalized response."""
        raise NotImplementedError

    @abstractmethod
    async def stream(self, *, request: InferenceRequest | None = None, model: str | None = None, prompt: str | None = None, **kwargs: Any) -> AsyncIterator[str]:
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
