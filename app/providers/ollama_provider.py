from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator

from datetime import datetime, timezone

from app.providers.base_provider import BaseProvider, ProviderModel, ProviderResponse
from app.schemas.inference_response import InferenceResponse, Usage
from app.schemas.request import ChatMessage, InferenceRequest


class OllamaProvider(BaseProvider):
    """Ollama provider implementation."""

    name = "ollama"

    def __init__(self, *, base_url: str | None = None) -> None:
        self.base_url = base_url or "http://localhost:11434"

    async def generate(self, *, request: InferenceRequest | None = None, model: str | None = None, prompt: str | None = None, **kwargs: Any) -> InferenceResponse:
        """Return a standardized response for the prompt."""
        request_obj = request or InferenceRequest(model=model or "", messages=[ChatMessage(role="user", content=prompt or "")])
        model_name = request_obj.model or model or ""
        prompt_text = prompt or self._extract_prompt(request_obj)
        created_at = datetime.now(timezone.utc)
        return InferenceResponse(
            id=f"chatcmpl-{model_name}",
            provider=self.name,
            model=model_name,
            text=f"[ollama:{model_name}] {prompt_text}",
            usage=Usage(prompt_tokens=max(1, len(prompt_text.split())), completion_tokens=max(1, len(prompt_text.split())), total_tokens=max(1, len(prompt_text.split())) * 2),
            finish_reason="stop",
            latency_ms=0.0,
            created=created_at,
            metadata={"base_url": self.base_url, "provider_version": "v1", "cached": False, **kwargs},
            request_id=kwargs.get("request_id"),
            raw_response=None,
        )

    async def stream(self, *, request: InferenceRequest | None = None, model: str | None = None, prompt: str | None = None, **kwargs: Any) -> AsyncIterator[str]:
        """Yield OpenAI-style streamed chunks for the completion."""
        request_obj = request or InferenceRequest(model=model or "", messages=[ChatMessage(role="user", content=prompt or "")])
        model_name = request_obj.model or model or ""
        prompt_text = prompt or self._extract_prompt(request_obj)
        text = f"[ollama:{model_name}] {prompt_text}"
        words = text.split()
        for index, word in enumerate(words):
            chunk = {
                "id": f"chatcmpl-{model_name}",
                "object": "chat.completion.chunk",
                "created": 0,
                "model": model_name,
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

    @staticmethod
    def _extract_prompt(request: InferenceRequest) -> str:
        if not request.messages:
            return ""
        last_message = request.messages[-1]
        return last_message.content

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
