from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator

from app.schemas.inference_response import InferenceResponse
from app.schemas.request import InferenceRequest


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

    @staticmethod
    def _extract_prompt(request: InferenceRequest) -> str:
        """Extract the user prompt from the request messages."""
        if not request.messages:
            return ""
        return request.messages[-1].content

    @abstractmethod
    async def generate(
        self,
        *,
        request: InferenceRequest | None = None,
        model: str | None = None,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> InferenceResponse:
        """Generate a completion from the provider and return a normalized response."""
        raise NotImplementedError

    @abstractmethod
    def stream(
        self,
        request: InferenceRequest | None = None,
        model: str | None = None,
        prompt: str | None = None,
        **kwargs: Any,
    ) -> AsyncIterator[InferenceResponse]:
        """Stream normalized InferenceResponse chunks from the provider."""
        raise NotImplementedError

    @abstractmethod
    async def health_check(self) -> bool:
        """Check whether the provider is healthy."""
        raise NotImplementedError

    @abstractmethod
    async def list_models(self) -> list[ProviderModel]:
        """List the models available from the provider."""
        raise NotImplementedError
