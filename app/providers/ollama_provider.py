from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator

from app.providers.base_provider import BaseProvider, ProviderModel, ProviderResponse


class OllamaProvider(BaseProvider):
    """Ollama provider implementation."""

    name = "ollama"

    def __init__(self, *, base_url: str | None = None) -> None:
        self.base_url = base_url or "http://localhost:11434"

    async def generate(self, *, model: str, prompt: str, **kwargs: Any) -> ProviderResponse:
        """Return a standardized response for the prompt."""
        return ProviderResponse(
            text=f"[ollama:{model}] {prompt}",
            model=model,
            provider=self.name,
            metadata={"base_url": self.base_url, **kwargs},
        )

    async def stream(self, *, model: str, prompt: str, **kwargs: Any) -> AsyncIterator[str]:
        """Yield OpenAI-style streamed chunks for the completion."""
        text = f"[ollama:{model}] {prompt}"
        words = text.split()
        for index, word in enumerate(words):
            chunk = {
                "id": f"chatcmpl-{model}",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": word + (" " if index < len(words) - 1 else "")},
                        "finish_reason": None,
                    }
                ],
            }
            yield f"data: {chunk!s}\n\n"
            await asyncio.sleep(0)  # pragma: no cover - pacing hook
        yield "data: [DONE]\n\n"

    async def health_check(self) -> bool:
        """Return True until a real network validation is implemented."""
        return True

    async def list_models(self) -> list[ProviderModel]:
        """Return a small set of example Ollama model metadata."""
        return [
            ProviderModel(
                id="llama3.1",
                provider=self.name,
                description="Ollama local Llama 3.1",
                context_window=8192,
                status="available",
            ),
            ProviderModel(
                id="mistral",
                provider=self.name,
                description="Ollama local Mistral",
                context_window=4096,
                status="available",
            ),
        ]
